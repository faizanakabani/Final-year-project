import asyncio
import re
import json
import os
import uuid
import io
import logging
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

# =====================================================
# ENV + SETTINGS
# =====================================================

os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

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

app = FastAPI()

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

        chunk_id = str(uuid.uuid4())

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

    collection.add(
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

        # ✅ STRICT MODE
        if (
            not results["documents"]
            or len(results["documents"][0]) == 0
        ):
            logger.warning("No context found. Blocking answer.")
            return {
                "response": "No relevant data found in knowledge base.",
                "sources": [],
            }

        context = "\n\n".join(results["documents"][0])

        # LLM CALL ONLY WHEN CONTEXT EXISTS
        chat_completion = await llm.chat.completions.create(
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
        )

        return {
            "response": chat_completion.choices[0].message.content,
            "sources": results["metadatas"][0],
        }

    except Exception as e:
        logger.error(e)
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