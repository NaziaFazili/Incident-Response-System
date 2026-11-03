# Incident-Response-System
uv run --no-project python -m scripts.setup_vectorstore


FastAPI	http://localhost:8000 uv run uvicorn app.main:app --reload --port 8000
Observability MCP Server	http://localhost:8080/sse

http://localhost:5678 n8n
http://localhost:5678/webhook-test/incident-alert
http://localhost:5678/webhook/incident-alert

For our current simulated Authentication API incident, HIST-001 should be a strong match because it mentions:
- SQL connection timeouts
- High API error rates
- Database connection pool exhaustion
- A recent deployment

Runbooks describe the steps engineers can follow to investigate and resolve common problems.
runbooks include remediation options
Our Remediation Agent will decide which options to recommend, and human approval will be required before executing any action.

1. Loads past_incidents.json and runbooks.json.
2. Converts each record into searchable text while preserving its document ID.
3. Generates embeddings using ChromaDB.
4. Stores the documents in a persistent local vector database.
5. Allows the Knowledge Agent to retrieve the most relevant documents.
For example, the query:
Find similar incidents involving authentication-api, SQL timeouts, and database connection pool exhaustion.

Should retrieve documents such as:
HIST-001 — Authentication API database connection pool exhaustion
RB-001   — Database Connection Pool Exhaustion
RB-002   — High API Error Rate

data/past_incidents.json
data/runbooks.json
          |
          ▼
 scripts/setup_vectorstore.py
          |
          ▼
   Prepare document text
          |
          ▼
   Generate embeddings
   (ChromaDB default)
          |
          ▼
       ChromaDB
    data/chroma_db/
          |
          ▼
     RAG Search Tool
          |
          ▼
     Knowledge Agent
          |
          | A2A
          ▼
     Coordinator