import logging
from pathlib import Path

import chromadb

logger = logging.getLogger(__name__)
from config.RAG_config import COLLECTION_NAME, VECTORSTORE_PATH

# PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# VECTORSTORE_PATH = PROJECT_ROOT / "data" / "chroma_db"

# COLLECTION_NAME = "incident_knowledge"


def search_knowledge(query: str) -> list[dict]:
    """
    Search historical incidents and runbooks using semantic similarity.

    Args:
        query: Description of the incident or problem.

    Returns:
        List of relevant historical incidents and runbooks.
    """

    logger.info("[KNOWLEDGE] Searching: %s", query)

    client = chromadb.PersistentClient(path=str(VECTORSTORE_PATH))

    collection = client.get_collection(name=COLLECTION_NAME)

    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(3, collection.count()),
    )

    documents = []

    for i, document in enumerate(results["documents"][0]):
        documents.append(
            {
                "id": results["ids"][0][i],
                "content": document,
                "metadata": results["metadatas"][0][i],
            }
        )

    logger.info("[KNOWLEDGE] Found %s matching documents", len(documents))

    return documents
