"""
Setup ChromaDB Vector Store for Incident Response Knowledge.

Loads historical incidents and runbooks, generates embeddings,
and stores documents in ChromaDB for RAG retrieval.
"""

import json
import logging
import os
from pathlib import Path

import chromadb

from config.RAG_config import COLLECTION_NAME, DATA_DIR, VECTORSTORE_PATH

logger = logging.getLogger(__name__)

# PROJECT_ROOT = Path(__file__).resolve().parent.parent
# DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
# # DATA_DIR = PROJECT_ROOT / "data"
# VECTORSTORE_PATH = DATA_DIR / "chroma_db"

# COLLECTION_NAME = "incident_knowledge"


def load_documents() -> tuple[list, list, list]:
    """Load historical incidents and runbooks."""

    documents = []
    ids = []
    metadatas = []

    # Load historical incidents
    with open(DATA_DIR / "past_incidents.json", encoding="utf-8") as file:
        incidents = json.load(file)

    for incident in incidents:
        documents.append(json.dumps(incident))
        ids.append(incident["incident_id"])

        metadatas.append(
            {
                "type": "incident",
                "service": incident["service"],
                "title": incident["title"],
            }
        )

    # Load runbooks
    with open(DATA_DIR / "runbooks.json", encoding="utf-8") as file:
        runbooks = json.load(file)

    for runbook in runbooks:
        documents.append(json.dumps(runbook))
        ids.append(runbook["runbook_id"])

        metadatas.append(
            {
                "type": "runbook",
                "title": runbook["title"],
            }
        )

    return documents, ids, metadatas


def create_vectorstore() -> None:
    """Create the ChromaDB vector store."""

    logger.info("Loading incident knowledge documents...")

    documents, ids, metadatas = load_documents()

    if not documents:
        logger.warning("No knowledge documents found.")
        return

    logger.info("Loaded %s documents", len(documents))

    # Step 1: Initialize ChromaDB
    VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(VECTORSTORE_PATH))

    # Step 2: Create collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Step 3: Generate embeddings and store documents
    # ChromaDB generates embeddings automatically when
    # documents are provided without explicit embeddings.
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    logger.info("Vector store created successfully.")
    logger.info("Collection: %s", COLLECTION_NAME)
    logger.info("Total documents: %s", collection.count())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_vectorstore()
