# =====================================================
# FORCE LOGGING (MUST BE FIRST LINES)
# =====================================================
import logging
import sys

# remove any logging created by other libraries
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.DEBUG,  # change to INFO later
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.info("✅ Logging initialized successfully")


# =====================================================
# IMPORTS
# =====================================================
import chromadb
from fastembed import TextEmbedding
from llm_client import llm
from pydantic import BaseModel


# -----------------------------
# RESPONSE MODEL
# -----------------------------
class Chat_response(BaseModel):
    chat_response: str
    link: str


# -----------------------------
# QUERY FILTER
# -----------------------------
def is_goa_query(query: str) -> bool:
    result = "goa" in query.lower()
    logger.info(f"Query validation: {result}")
    return result


# -----------------------------
# DATABASE QUERY (STRICT)
# -----------------------------
SIMILARITY_THRESHOLD = 0.75


def query_database(query_text: str, collection, embedding_model):

    logger.info("Generating embedding...")
    query_embedding = list(embedding_model.embed(query_text))[0]

    logger.info("Querying ChromaDB...")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=["documents", "distances"]
    )

    if not results or not results["documents"]:
        logger.warning("No documents returned from DB")
        return []

    documents = results["documents"][0]
    distances = results["distances"][0]

    valid_docs = []

    logger.info("Filtering documents by similarity...")

    for doc, dist in zip(documents, distances):
        similarity = 1 - dist
        logger.debug(f"Similarity score: {similarity:.3f}")

        if similarity >= SIMILARITY_THRESHOLD:
            valid_docs.append(doc)

    logger.info(f"Valid documents found: {len(valid_docs)}")

    return valid_docs


# -----------------------------
# LLM RESPONSE
# -----------------------------
def generate_response_with_llm(query_text: str, context_sentences: list):

    context = "\n".join(context_sentences)

    logger.info("Sending context to LLM...")
    logger.debug(f"\n===== CONTEXT SENT TO LLM =====\n{context}\n===============================")

    messages = [
        {
            "role": "system",
            "content": """
You are a STRICT Assistant.

RULES:
- Answer ONLY using CONTEXT.
- CONTEXT is the ONLY truth.
- If answer not present → REFUSE.

REFUSAL:
"I couldn't find any information related to this query."
"""
        },
        {
            "role": "user",
            "content": f"""
Query:
{query_text}

Context:
{context}
"""
        }
    ]

    response = llm.chat.completions.create(
        messages=messages,
        model="llama-3.1-8b-instant"
    )

    logger.info("LLM response received.")
    return response


# -----------------------------
# MAIN LOOP
# -----------------------------
def main():

    logger.info("🚀 Starting Goa Heritage Assistant")

    chroma_client = chromadb.PersistentClient(path=".chromadb")
    collection = chroma_client.get_or_create_collection(name="sentences")
    embedding_model = TextEmbedding()

    while True:
        query_text = input("Enter your query: ")

        if query_text.lower() == "exit":
            logger.info("Exiting program.")
            break

        if not is_goa_query(query_text):
            print("Only Goa-related queries are allowed.")
            continue

        context = query_database(query_text, collection, embedding_model)

        # STRICT BLOCK
        if not context:
            logger.warning("No valid context found.")
            print(
                "I couldn't find any information related to this in the provided Goa database."
            )
            continue

        response = generate_response_with_llm(query_text, context)

        print("\n🤖 Response:\n")
        print(response.choices[0].message.content)


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    main()