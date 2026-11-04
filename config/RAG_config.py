"""
Configuration for RAG
"""

import os
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))

VECTORSTORE_PATH = DATA_DIR / "chroma_db"

COLLECTION_NAME = "incident_knowledge"
