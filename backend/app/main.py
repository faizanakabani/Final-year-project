import asyncio
import hashlib
import re
import json
import os
import uuid
import io
import logging
from pathlib import Path
from typing import List
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import uvicorn

from llm_client import llm
from supabase import create_client, Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

# =====================================================
# ENV + SETTINGS
# =====================================================

os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Global variables for cleanup
_supabase_channel = None

async def handle_content_changes(payload):
    logger.info(f"Content changed: {payload}")
    await sync_supabase_data()

# =====================================================
# LOGGING CONFIG
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("RAG-API")

# =====================================================
# FASTAPI INIT
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _supabase_channel, scheduler
    
    # Startup
    try:
        await ingest_heritage_pdf()
        logger.info("Heritage PDF ingestion completed")
    except Exception as e:
        logger.error(f"Failed to ingest heritage PDF during startup: {e}")
    
    try:
        await sync_supabase_data()
        logger.info("Supabase sync completed")
    except Exception as e:
        logger.error(f"Failed to sync Supabase data during startup: {e}")
    
    try:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(sync_supabase_data, 'interval', hours=1)
        scheduler.start()
        logger.info("Scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
    
    # Setup Supabase subscription (non-blocking)
    try:
        _supabase_channel = supabase.channel('content_changes')
        _supabase_channel.on('postgres_changes', {'event': '*', 'schema': 'public', 'table': 'content'}, lambda payload: asyncio.create_task(handle_content_changes(payload)))
        await asyncio.wait_for(supabase.subscribe(_supabase_channel), timeout=5.0)
        logger.info("Supabase subscription established")
    except asyncio.TimeoutError:
        logger.warning("Supabase subscription timed out, continuing without it")
    except Exception as e:
        logger.error(f"Failed to setup Supabase subscription: {e}")
    
    yield
    
    # Shutdown
    if _supabase_channel:
        try:
            await supabase.unsubscribe(_supabase_channel)
            logger.info("Supabase subscription closed")
        except Exception as e:
            logger.error(f"Error during unsubscribe: {e}")
    
    if 'scheduler' in globals():
        try:
            scheduler.shutdown()
            logger.info("Scheduler shut down")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# CHROMADB (PERSISTENT CLIENT ✅)
# =====================================================

collection_name = "final-year"

os.makedirs("./chroma_storage", exist_ok=True)

logger.info("Initializing Persistent ChromaDB...")

chroma_client = chromadb.PersistentClient(
    path="./chroma_storage"
)

collection = chroma_client.get_or_create_collection(
    name=collection_name
)

logger.info("ChromaDB ready.")

# =====================================================
# EMBEDDINGS + SPLITTER
# =====================================================

embedding_function = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100
)

# =====================================================
# MODELS
# =====================================================

class ChatResponse(BaseModel):
    chat_response: str
    link: str


class IngestWebRequest(BaseModel):
    url: str
    knowledge_id: str
    user_id: str


class QueryRequest(BaseModel):
    query: str
    knowledge_id: str
    user_id: str


# =====================================================
# SYNC SUPABASE DATA
# =====================================================

async def sync_supabase_data():
    try:
        # Fetch content
        response = supabase.table('content').select('*').execute()
        contents = response.data

        for content in contents:
            text = f"{content.get('title', '')} {content.get('description', '')} {content.get('longDescription', '')} {content.get('howTo', '')} {content.get('whatTo', '')}"
            if not text.strip():
                continue

            # Split and store
            chunks = text_splitter.split_text(text)
            valid_chunks = [c for c in chunks if c.strip()]

            if not valid_chunks:
                continue

            embeddings = []
            ids = []
            metadatas = []

            for idx, chunk in enumerate(valid_chunks):
                embedding = embedding_function.embed_query(chunk)
                chunk_id = f"supabase:{content.get('id', uuid.uuid4())}:{idx}"

                metadata = {
                    "knowledge_id": "goa",
                    "user_id": "admin",
                    "content_id": str(content.get('id', '')),
                    "title": content.get('title', ''),
                    "category": content.get('category', ''),
                    "latitude": str(content.get('latitude', '')),
                    "longitude": str(content.get('longitude', '')),
                    "imageUrl": content.get('imageUrl', ''),
                    "createdAt": content.get('createdAt', ''),
                }

                embeddings.append(embedding)
                ids.append(chunk_id)
                metadatas.append(metadata)

            # Upsert to Chroma
            collection.upsert(
                documents=valid_chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids,
            )

        logger.info(f"Synced {len(contents)} content items from Supabase")

    except Exception as e:
        logger.error(f"Error syncing Supabase data: {e}")


async def ingest_heritage_pdf():
    try:
        project_root = Path(__file__).resolve().parent.parent
        pdf_path = project_root / "goa_heritage_structures_notes (1).pdf"

        if not pdf_path.exists():
            logger.warning(f"PDF not found at {pdf_path}")
            return

        with pdf_path.open('rb') as f:
            contents = f.read()

        reader = PdfReader(io.BytesIO(contents))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        knowledge_id = "goa"
        user_id = "admin"

        await store_text(text, knowledge_id, user_id, "goa_heritage_structures_notes.pdf", is_url=False)

        logger.info("Ingested heritage PDF")

    except Exception as e:
        logger.error(f"Error ingesting heritage PDF: {e}")


# =====================================================
# STORE TEXT
# =====================================================

async def store_text(text, knowledge_id, user_id, link=None, is_url=True):

    chunks = text_splitter.split_text(text)
    valid_chunks = [c for c in chunks if c.strip()]

    if not valid_chunks:
        logger.warning("No valid chunks found.")
        return

    embeddings = []
    ids = []
    metadatas = []

    for chunk in valid_chunks:
        embedding = embedding_function.embed_query(chunk)

        chunk_hash = hashlib.sha256(chunk.encode('utf-8')).hexdigest()
        chunk_id = f"{knowledge_id}:{user_id}:{chunk_hash}"

        metadata = {
            "knowledge_id": knowledge_id,
            "user_id": user_id,
            "chunk_id": chunk_id,
        }

        if is_url:
            metadata["link"] = link
        else:
            metadata["file_name"] = link

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
# WEB SCRAPER
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

# ---------------- INGEST WEB ----------------

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


# ---------------- INGEST PDF ----------------

@router.post("/ingestPDF")
async def ingest_pdf(
    knowledge_id: str,
    user_id: str,
    file: UploadFile = File(...)
):

    try:
        contents = await file.read()
        reader = PdfReader(io.BytesIO(contents))

        text = ""
        for page in reader.pages:
            text += page.extract_text()

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


# ---------------- QUERY (STRICT RAG ✅) ----------------

@router.post("/query")
async def query(request: QueryRequest):

    try:
        logger.info(f"Query received: {request.query}")

        embedded_query = embedding_function.embed_query(request.query)

        results = collection.query(
            query_embeddings=[embedded_query],
            n_results=5,
            where={
                "$and": [
                    {"knowledge_id": request.knowledge_id},
                    {"user_id": request.user_id},
                ]
            },
            include=["documents", "metadatas"],
        )

        if not results["documents"] or len(results["documents"][0]) == 0:
            logger.warning("No context found with strict metadata filter. Trying fallback search.")
            results = collection.query(
                query_embeddings=[embedded_query],
                n_results=5,
                where={"user_id": request.user_id},
                include=["documents", "metadatas"],
            )

        if not results["documents"] or len(results["documents"][0]) == 0:
            logger.warning("No context found after fallback search. Blocking answer.")
            return {
                "response": "No relevant data found in knowledge base.",
                "sources": [],
            }

        context = "\n\n".join(results["documents"][0])

        # LLM CALL ONLY WHEN CONTEXT EXISTS
        try:
            logger.info("Calling LLM API...")
            chat_completion = await asyncio.wait_for(
                llm.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Answer ONLY using provided context. "
                                "If answer is not present, reply exactly: "
                                "'No relevant data found in knowledge base.'"
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Context:\n{context}\n\nQuestion:{request.query}",
                        },
                    ],
                ),
                timeout=25.0  # 25 second timeout for LLM call
            )
            logger.info("LLM API call completed successfully")
            return {
                "response": chat_completion.choices[0].message.content,
                "sources": results["metadatas"][0],
            }
        except asyncio.TimeoutError:
            logger.error("LLM API call timed out after 25 seconds")
            raise HTTPException(
                status_code=504,
                detail="LLM API call timed out. Please try again."
            )
        except Exception as llm_error:
            logger.error(f"LLM API error: {llm_error}")
            raise HTTPException(
                status_code=500,
                detail=f"LLM API error: {str(llm_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# APP START
# =====================================================

app.include_router(router)

def main():
    logger.info("Starting API on 127.0.0.1:9000 (reload=True)...")
    uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)


if __name__ == "__main__":
    main()