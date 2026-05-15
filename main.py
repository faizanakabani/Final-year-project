# main.py

import asyncio
import hashlib
import re
import os
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from langchain_community.embeddings import SentenceTransformerEmbeddings
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import uvicorn

from llm_client import llm
from structured_queries import build_structured_query_response
from supabase import create_client, Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ModuleNotFoundError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

# =====================================================
# ENV + SETTINGS
# =====================================================

os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("SUPABASE credentials missing in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================================================
# LOGGING CONFIG
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("RAG-API")

# =====================================================
# GLOBALS
# =====================================================

_supabase_channel = None
scheduler = None

# =====================================================
# FASTAPI INIT
# =====================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _supabase_channel, scheduler

    # Ingest PDF
    try:
        await ingest_heritage_pdf()
        logger.info("Heritage PDF ingestion completed")
    except Exception as e:
        logger.error(f"Failed to ingest heritage PDF: {e}")

    # Sync Supabase
    try:
        await sync_supabase_data()
        logger.info("Supabase sync completed")
    except Exception as e:
        logger.error(f"Supabase sync failed: {e}")

    # Scheduler
    try:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(sync_supabase_data, "interval", hours=1)
        scheduler.start()
        logger.info("Scheduler started")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")

    yield

    # Shutdown
    try:
        if scheduler:
            scheduler.shutdown()
            logger.info("Scheduler shut down")
    except Exception as e:
        logger.error(f"Scheduler shutdown failed: {e}")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# CHROMADB
# =====================================================

collection_name = "final-year"
HERITAGE_PDF_NAME = "goa_heritage_structures_notes.pdf"


def initialize_chroma_collection():
    storage_path = Path("./chroma_storage")
    storage_path.mkdir(exist_ok=True)

    logger.info("Initializing Persistent ChromaDB...")

    try:
        client = chromadb.PersistentClient(path=str(storage_path))
        active_collection = client.get_or_create_collection(name=collection_name)
        logger.info("ChromaDB ready.")
        return client, active_collection
    except BaseException as e:
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise

        backup_path = storage_path.with_name(
            f"{storage_path.name}_corrupt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        logger.error(f"ChromaDB failed to open: {e}")

        try:
            if storage_path.exists():
                storage_path.rename(backup_path)
                logger.warning(f"Moved corrupt Chroma storage to {backup_path}")

            storage_path.mkdir(exist_ok=True)
            client = chromadb.PersistentClient(path=str(storage_path))
            active_collection = client.get_or_create_collection(name=collection_name)
            logger.info("ChromaDB rebuilt with empty local index.")
            return client, active_collection
        except BaseException as rebuild_error:
            if isinstance(rebuild_error, (KeyboardInterrupt, SystemExit)):
                raise

            logger.error(
                "ChromaDB disabled after rebuild failed. "
                f"Supabase direct retrieval will still work. Error: {rebuild_error}"
            )
            return None, None


chroma_client, collection = initialize_chroma_collection()

# =====================================================
# EMBEDDINGS
# =====================================================

embedding_function = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100,
)

VECTOR_TOP_K = 25
LEXICAL_TOP_K = 15
SUPABASE_TOP_K = 12
CONTEXT_TOP_K = 12
MAX_CONTEXT_CHARS = 12000

TEXT_FIELD_PRIORITY = [
    "title",
    "name",
    "description",
    "shortDescription",
    "longDescription",
    "category",
    "howTo",
    "whatTo",
    "history",
    "architecture",
    "architect",
    "artist",
    "designer",
    "author",
]

SKIP_TEXT_FIELDS = {
    "imageUrl",
    "images",
    "latitude",
    "longitude",
    "createdAt",
    "updatedAt",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "about",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "where",
    "who",
    "with",
}

# =====================================================
# MODELS
# =====================================================


class IngestWebRequest(BaseModel):
    url: str
    knowledge_id: str
    user_id: str


class QueryRequest(BaseModel):
    query: str
    knowledge_id: str
    user_id: str

# =====================================================
# RETRIEVAL HELPERS
# =====================================================


def _label_for_field(field: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", field).replace("_", " ").title()


def _stringify_content_value(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (int, float, bool)):
        return str(value)

    if isinstance(value, list):
        parts = [
            _stringify_content_value(item)
            for item in value
            if not isinstance(item, (dict, list))
        ]
        return ", ".join(part for part in parts if part)

    return ""


def build_searchable_content_text(content: Dict[str, Any]) -> str:
    lines = []
    used_fields = set()

    for field in TEXT_FIELD_PRIORITY:
        value = _stringify_content_value(content.get(field))
        if value:
            lines.append(f"{_label_for_field(field)}: {value}")
            used_fields.add(field)

    for field, raw_value in content.items():
        if field in used_fields or field in SKIP_TEXT_FIELDS:
            continue

        value = _stringify_content_value(raw_value)
        if not value:
            continue

        if value.startswith("http://") or value.startswith("https://"):
            continue

        lines.append(f"{_label_for_field(field)}: {value}")

    return "\n".join(lines)


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    return re.sub(r"[^a-z0-9]+", " ", lowered).strip()


def _tokens_for_query(query: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", query.lower())
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def _metadata_text(metadata: Dict[str, Any]) -> str:
    values = []
    for key in ("title", "name", "category", "file_name", "link", "source"):
        value = metadata.get(key)
        if value:
            values.append(str(value))
    return " ".join(values)


def _lexical_score(query: str, document: str, metadata: Dict[str, Any]) -> float:
    query_norm = _normalize_text(query)
    tokens = _tokens_for_query(query)

    if not query_norm or not tokens:
        return 0.0

    document_norm = _normalize_text(f"{document} {_metadata_text(metadata)}")
    document_tokens = set(document_norm.split())
    title_norm = _normalize_text(str(metadata.get("title", "")))

    score = 0.0

    if f" {query_norm} " in f" {document_norm} ":
        score += 8.0

    if title_norm and f" {query_norm} " in f" {title_norm} ":
        score += 12.0

    token_hits = sum(1 for token in tokens if token in document_tokens)
    score += token_hits

    if tokens and token_hits == len(tokens):
        score += 4.0

    if title_norm:
        title_tokens = set(title_norm.split())
        title_hits = sum(1 for token in tokens if token in title_tokens)
        score += title_hits * 2.0

    return score


def _candidate_key(doc_id: str, document: str, metadata: Dict[str, Any]) -> str:
    if doc_id:
        return doc_id

    metadata_id = metadata.get("chunk_id") or metadata.get("id")
    if metadata_id:
        return str(metadata_id)

    return hashlib.sha256(document.encode("utf-8")).hexdigest()


def _add_candidate(
    candidates: Dict[str, Dict[str, Any]],
    doc_id: str,
    document: str,
    metadata: Dict[str, Any],
    score: float,
) -> None:
    key = _candidate_key(doc_id, document, metadata)
    existing = candidates.get(key)

    if existing:
        existing["score"] = max(existing["score"], score)
        return

    candidates[key] = {
        "document": document,
        "metadata": metadata or {},
        "score": score,
    }


def _get_matching_documents(knowledge_id: str, user_id: str) -> Dict[str, Any]:
    if collection is None:
        return {"documents": [], "metadatas": [], "ids": []}

    return collection.get(
        where={
            "$and": [
                {"knowledge_id": knowledge_id},
                {"user_id": user_id},
            ]
        },
        include=["documents", "metadatas"],
    )


def _content_metadata(content: Dict[str, Any], chunk_id: str) -> Dict[str, Any]:
    return {
        "knowledge_id": "goa",
        "user_id": "admin",
        "chunk_id": chunk_id,
        "content_id": str(content.get("id", "")),
        "title": _stringify_content_value(content.get("title")),
        "category": _stringify_content_value(content.get("category")),
        "source": "supabase",
    }


def _fetch_supabase_content_rows() -> List[Dict[str, Any]] | None:
    try:
        response = supabase.table("content").select("*").execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Supabase content fetch failed: {e}")
        return None


def _add_supabase_content_candidates(
    candidates: Dict[str, Dict[str, Any]],
    query_text: str,
) -> int:
    rows = _fetch_supabase_content_rows()
    if rows is None:
        logger.error("Supabase direct retrieval failed")
        return 0

    scored_rows = []

    for content in rows:
        document = build_searchable_content_text(content)
        if not document.strip():
            continue

        content_id = str(content.get("id", "unknown"))
        doc_id = f"supabase-row:{content_id}"
        metadata = _content_metadata(content, doc_id)
        score = _lexical_score(query_text, document, metadata)

        if score <= 0:
            continue

        scored_rows.append((score, doc_id, document, metadata))

    scored_rows.sort(key=lambda item: item[0], reverse=True)

    for score, doc_id, document, metadata in scored_rows[:SUPABASE_TOP_K]:
        _add_candidate(candidates, doc_id, document, metadata, score + 20.0)

    logger.info(
        "Supabase direct retrieval found %s lexical matches for '%s'",
        len(scored_rows),
        query_text,
    )

    return len(scored_rows)


def retrieve_relevant_context(
    query_text: str,
    knowledge_id: str,
    user_id: str,
) -> Tuple[str, List[Dict[str, Any]]]:
    candidates: Dict[str, Dict[str, Any]] = {}
    where_filter = {
        "$and": [
            {"knowledge_id": knowledge_id},
            {"user_id": user_id},
        ]
    }

    all_docs = _get_matching_documents(knowledge_id, user_id)
    docs = all_docs.get("documents", []) or []
    metadatas = all_docs.get("metadatas", []) or []
    ids = all_docs.get("ids", []) or []

    supabase_match_count = _add_supabase_content_candidates(candidates, query_text)

    lexical_candidates = []

    if docs:
        vector_count = max(1, min(VECTOR_TOP_K, len(docs)))
        embedded_query = embedding_function.embed_query(query_text)

        vector_results = collection.query(
            query_embeddings=[embedded_query],
            n_results=vector_count,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        vector_docs = vector_results.get("documents", [[]])[0] or []
        vector_metadatas = vector_results.get("metadatas", [[]])[0] or []
        vector_distances = vector_results.get("distances", [[]])[0] or []
        vector_ids = vector_results.get("ids", [[]])[0] or []

        for rank, document in enumerate(vector_docs):
            metadata = vector_metadatas[rank] if rank < len(vector_metadatas) else {}
            distance = vector_distances[rank] if rank < len(vector_distances) else 1.0
            doc_id = vector_ids[rank] if rank < len(vector_ids) else ""
            lexical = _lexical_score(query_text, document, metadata or {})
            vector_score = max(0.0, 1.0 / (1.0 + float(distance)))
            rank_boost = (vector_count - rank) / max(vector_count, 1)
            score = vector_score + rank_boost + lexical
            _add_candidate(candidates, doc_id, document, metadata or {}, score)

        for idx, document in enumerate(docs):
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            score = _lexical_score(query_text, document, metadata or {})
            if score <= 0:
                continue

            doc_id = ids[idx] if idx < len(ids) else ""
            lexical_candidates.append((score, doc_id, document, metadata or {}))

    lexical_candidates.sort(key=lambda item: item[0], reverse=True)

    for score, doc_id, document, metadata in lexical_candidates[:LEXICAL_TOP_K]:
        _add_candidate(candidates, doc_id, document, metadata, score + 10.0)

    ranked_candidates = sorted(
        candidates.values(),
        key=lambda item: item["score"],
        reverse=True,
    )

    selected = []
    context_parts = []
    total_chars = 0

    for index, candidate in enumerate(ranked_candidates[:CONTEXT_TOP_K], start=1):
        document = candidate["document"].strip()
        metadata = candidate["metadata"]

        if not document:
            continue

        title = (
            metadata.get("title")
            or metadata.get("file_name")
            or metadata.get("link")
            or f"Source {index}"
        )
        source_block = f"Source {index}: {title}\n{document}"

        if total_chars + len(source_block) > MAX_CONTEXT_CHARS:
            continue

        context_parts.append(source_block)
        selected.append(metadata)
        total_chars += len(source_block)

    logger.info(
        "Retrieved %s context chunks for query '%s' (%s lexical matches)",
        len(selected),
        query_text,
        len(lexical_candidates) + supabase_match_count,
    )

    return "\n\n".join(context_parts), selected

# =====================================================
# STORE TEXT
# =====================================================


async def store_text(text, knowledge_id, user_id, link=None, is_url=True):
    if collection is None:
        logger.warning("Skipping local Chroma storage because ChromaDB is unavailable.")
        return

    chunks = text_splitter.split_text(text)
    valid_chunks = [c for c in chunks if c.strip()]

    if not valid_chunks:
        return

    embeddings = []
    ids = []
    metadatas = []

    for chunk in valid_chunks:
        embedding = embedding_function.embed_query(chunk)
        chunk_hash = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
        chunk_id = f"{knowledge_id}:{user_id}:{chunk_hash}"

        metadata = {
            "knowledge_id": knowledge_id,
            "user_id": user_id,
            "chunk_id": chunk_id,
        }

        if is_url:
            metadata["link"] = link or ""
        else:
            metadata["file_name"] = link or ""

        embeddings.append(embedding)
        ids.append(chunk_id)
        metadatas.append(metadata)

    collection.upsert(
        documents=valid_chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    logger.info(f"Stored {len(valid_chunks)} chunks.")

# =====================================================
# PDF INGESTION
# =====================================================


async def ingest_heritage_pdf():
    try:
        project_root = Path(__file__).resolve().parent.parent
        pdf_path = project_root / HERITAGE_PDF_NAME

        if not pdf_path.exists():
            logger.warning(f"PDF not found: {pdf_path}")
            return

        with pdf_path.open("rb") as f:
            contents = f.read()

        reader = PdfReader(io.BytesIO(contents))
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        if collection is not None:
            existing = collection.get(
                where={
                    "$and": [
                        {"knowledge_id": "goa"},
                        {"user_id": "admin"},
                        {"file_name": HERITAGE_PDF_NAME},
                    ]
                },
                include=[],
            )
            existing_ids = existing.get("ids", []) or []
            if existing_ids:
                collection.delete(ids=existing_ids)
                logger.info(
                    "Deleted %s existing chunks for %s",
                    len(existing_ids),
                    HERITAGE_PDF_NAME,
                )

        await store_text(
            text=text,
            knowledge_id="goa",
            user_id="admin",
            link=HERITAGE_PDF_NAME,
            is_url=False,
        )

        logger.info("PDF ingested successfully")

    except Exception as e:
        logger.error(f"PDF ingestion failed: {e}")

# =====================================================
# SUPABASE SYNC
# =====================================================


async def sync_supabase_data():
    try:
        if collection is None:
            logger.warning(
                "Skipping Supabase-to-Chroma sync because ChromaDB is unavailable. "
                "Queries will use direct Supabase retrieval."
            )
            return

        response = supabase.table("content").select("*").execute()
        contents = response.data or []

        for content in contents:
            text = build_searchable_content_text(content)

            if not text.strip():
                continue

            chunks = text_splitter.split_text(text)

            for idx, chunk in enumerate(chunks):
                embedding = embedding_function.embed_query(chunk)
                chunk_id = f"supabase:{content.get('id')}:{idx}"
                metadata = _content_metadata(content, chunk_id)

                collection.upsert(
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    ids=[chunk_id],
                )

        logger.info(f"Synced {len(contents)} content items")

    except Exception as e:
        logger.error(f"Supabase sync failed: {e}")

# =====================================================
# SCRAPER
# =====================================================


async def scrape_page(
    crawler,
    url,
    visited_urls,
    base_url,
    base_domain,
    depth,
    max_depth,
    knowledge_id,
    user_id,
):
    if url in visited_urls or depth > max_depth:
        return

    visited_urls.add(url)

    try:
        logger.info(f"Scraping: {url}")

        result = await crawler.arun(url=url)
        markdown_content = result.markdown
        cleaned = re.sub(r"http[s]?://\\S+", "", markdown_content)

        await store_text(
            cleaned,
            knowledge_id,
            user_id,
            link=url,
            is_url=True,
        )

        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", markdown_content)

        for _, link_url in links:
            absolute_url = urljoin(base_url, link_url)
            parsed = urlparse(absolute_url)

            if parsed.netloc == base_domain:
                await scrape_page(
                    crawler,
                    absolute_url,
                    visited_urls,
                    base_url,
                    base_domain,
                    depth + 1,
                    max_depth,
                    knowledge_id,
                    user_id,
                )

    except Exception as e:
        logger.error(f"Scrape error {url}: {e}")

# =====================================================
# ROUTER
# =====================================================


router = APIRouter()

# =====================================================
# INGEST WEB
# =====================================================


@router.post("/ingestWeb")
async def ingest_web(request: IngestWebRequest):
    visited_urls = set()
    base_domain = urlparse(request.url).netloc

    async with AsyncWebCrawler() as crawler:
        await scrape_page(
            crawler,
            request.url,
            visited_urls,
            request.url,
            base_domain,
            0,
            3,
            request.knowledge_id,
            request.user_id,
        )

    return {"status": "success"}

# =====================================================
# INGEST PDF
# =====================================================


@router.post("/ingestPDF")
async def ingest_pdf(
    knowledge_id: str,
    user_id: str,
    file: UploadFile = File(...),
):
    try:
        contents = await file.read()
        reader = PdfReader(io.BytesIO(contents))
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        await store_text(
            text,
            knowledge_id,
            user_id,
            file.filename,
            is_url=False,
        )

        return {"status": "success"}

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# QUERY
# =====================================================


@router.post("/query")
async def query(request: QueryRequest):
    try:
        logger.info(f"Query received: {request.query}")

        content_rows = _fetch_supabase_content_rows()
        if content_rows is not None:
            structured_response = build_structured_query_response(
                request.query,
                content_rows,
            )
            if structured_response:
                response_text, sources = structured_response
                return {
                    "response": response_text,
                    "sources": sources,
                }

        context, sources = retrieve_relevant_context(
            request.query,
            request.knowledge_id,
            request.user_id,
        )

        if not context:
            return {
                "response": "No relevant data found in knowledge base.",
                "sources": [],
            }

        logger.info("Calling LLM API...")

        chat_completion = await asyncio.wait_for(
            llm.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Goa heritage assistant. Answer only using "
                            "the provided context. If the context contains a "
                            "direct or closely related answer, use it. If the "
                            "answer is not present, reply exactly: "
                            "'No relevant data found in knowledge base.' "
                            "Do not mention sources unless the user asks."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {request.query}",
                    },
                ],
            ),
            timeout=25.0,
        )

        logger.info("LLM API success")

        return {
            "response": chat_completion.choices[0].message.content,
            "sources": sources,
        }

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="LLM API timed out.",
        )

    except Exception as e:
        logger.error(f"Query error: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

# =====================================================
# APP START
# =====================================================


app.include_router(router)


def main():
    logger.info("Starting API on 127.0.0.1:9000")

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=9000,
        reload=True,
    )


if __name__ == "__main__":
    main()
