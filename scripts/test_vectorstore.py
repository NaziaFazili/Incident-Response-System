"""
Test ChromaDB knowledge retrieval.
"""

import chromadb

from scripts.setup_vectorstore import (
    COLLECTION_NAME,
    VECTORSTORE_PATH,
)


def test_search():
    client = chromadb.PersistentClient(path=str(VECTORSTORE_PATH))

    collection = client.get_collection(name=COLLECTION_NAME)

    query = (
        "Authentication API SQL connection timeouts "
        "and database connection pool exhaustion"
    )

    results = collection.query(
        query_texts=[query],
        n_results=3,
    )

    print("\nSearch Query:", query)
    print("\nMatching Documents:\n")

    for doc_id, metadata in zip(
        results["ids"][0],
        results["metadatas"][0],
    ):
        print(f"ID: {doc_id}")
        print(f"Title: {metadata['title']}")
        print(f"Type: {metadata['type']}")
        print("-" * 40)


if __name__ == "__main__":
    test_search()
