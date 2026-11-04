# Multi-Agent Incident Response System

A local demonstration of an AI-assisted incident-response pipeline. 
An incident alert can enter through **n8n** or a **direct Coordinator test prompt**. The Coordinator delegates investigation to Monitoring and Knowledge Agents, generates an investigation summary, and requests an HTN remediation plan. LangGraph human approval is required before simulated remediation execution.

> ** Remediation is simulated; the application does not roll back real deployments or restart production services.**

## Architecture

```text
n8n Webhook → IF (High Severity And Error rate > Threshold (10%)) 
                                 ↓ 
                        FastAPI POST /api/incidents 
                          (Create new incident + trigger Coordinator Agent)
                                 ↓
                           Coordinator (A2A)
                                 ↓
                    Monitoring   +      Knowledge (parallel)
(MCP tools logs/metrics/deployments)    ( RAG past_incidents/runbooks )
                                 ↓
                         Summary Agent
                                 ↓
                    Remediation Agent (HTN)
                                 ↓
                     LangGraph interrupt()
                                 ↓
                  Human approval HTML page
                       ↙             ↘
                   Approve           Reject
                      ↓                 ↓
               Simulated action     No execution
```

The Coordinator can also be invoked directly using the test runner, without n8n.

## Prerequisites

- **Python 3.11** (the project was developed using 3.11.17) and uv.
- Project dependencies and model/API credentials configured for the Google ADK/A2A, MCP and RAG components.
- **Docker Desktop** and **n8n** for the optional webhook-driven entry point.
- A modern browser for FastAPI Swagger and the approval page.

## Initial setup

1. Open the Project.
2. Configure Environment Variables:
   Update the existing .env file with your credentials and settings:

      GOOGLE_API_KEY=your_google_api_key
      GEMINI_MODEL=your_gemini_model
      MCP_SERVER_URL=http://localhost:8080/sse
3. Configure Agent Settings:
   Check the configuration files in the config/ folder. In agents_config, configure:

      INCIDENT_API_BASE_URL — FastAPI server URL (for example, http://localhost:8000).
      Agent URLs and ports for all four agents: Knowledge (10020), Monitoring (10021), Coordinator (10022), and Remediation (10023).
4. Install Python Dependencies (Make sure your project's virtual environment is active before running the command)
   uv pip install -r requirements.txt

5. Initialize ChromaDB
   Run the project's ChromaDB setup script to load historical incidents and runbooks into the knowledge base:
   uv run --no-project python -m scripts.setup_vectorstore

## Start the services

Use **separate terminals** in the project root:

**Terminal 1 — MCP server** (typically port `8080`):

```
uv run --no-project python -m mcp_server.server
```

**Terminal 2 — FastAPI** (port `8000`):

```
uv run --no-project uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 3 — A2A agent servers:**

```powershell
uv run --no-project python run_agents.py --mode start
```

Expected local A2A ports (check your agent configuration if different):

| Agent | Port |
| --- | ---: |
| Knowledge | 10020 |
| Monitoring | 10021 |
| Coordinator | 10022 |
| Remediation | 10023 |

Useful pages:

- FastAPI docs: <http://localhost:8000/docs>
- HITL approval UI: <http://localhost:8000/approval>
- n8n UI: <http://localhost:5678>

## Option A — Direct Coordinator test (no n8n)

This is the quickest way to demonstrate the agent workflow.

1. Start the **MCP server** and **FastAPI** as above.
2. **Do not separately start the A2A servers** for this test; the test runner starts them.
3. In `run_agents.py`, locate `test_agents()` → `["coordinator"]`. Change the incident ID or test description if desired.
4. Run:

   ```powershell
   uv run --no-project python run_agents.py --mode test --agent coordinator
   ```

5. Confirm Monitoring, Knowledge, Summary and Remediation agents produce results and FastAPI logs an approval request with `AWAITING_APPROVAL`.
6. Open <http://localhost:8000/approval>, enter the **exact incident ID shown in the HITL logs**, then choose **Approve Remediation** or **Reject Remediation**.
7. On approval, check for `[REMEDIATION] Simulating ...` in the FastAPI logs. On rejection, confirm there is **no remediation execution**.


## Option B — n8n webhook → FastAPI → Coordinator

1. Start MCP, FastAPI, as shown above.
   Start **A2A servers using
   
   ```powershell
   uv run --no-project python run_agents.py --mode start
   ```
2. Start your existing n8n Docker container (if it is stopped):

   ```powershell
   docker start n8n
   ```

3. Open <http://localhost:5678> and import the workflow JSON supplied with the project.
   Select the **Incident Alert Workflow**. 
4. Verify these n8n connections:

   ```text
   Webhook (POST /incident-alert)
       ↓
   IF: body.severity equals HIGH AND error_rate_pct > 10
       ↓ True
   Send Incident to FastAPI (POST /api/incidents)
   ```

5. Since n8n runs **inside Docker**, use this HTTP Request URL:

   ```text
   http://host.docker.internal:8000/api/incidents
   ```

6. Open the Webhook node and confirm the exact test webhook URL displayed by n8n. Execute the workflow.
   A typical URL is:

   ```text
   http://localhost:5678/webhook-test/incident-alert
   ```

7. Send a Test Incident Alert Using Postman:
   Open Postman and create a new HTTP request.
   Configure the request:
      Method: POST
      URL: http://localhost:5678/webhook-test/incident-alert
      Headers: Content-Type: application/json
      Body: Select raw → JSON.
   Enter the following sample alert in the request body:
   ```text   
      {
      "service": "authentication-api",
      "alert_type": "HIGH_ERROR_RATE",
      "severity": "HIGH",
      "detail": "Authentication API error rate exceeded 10%",
      "error_rate_pct" : 18.5,
      "threshold": 10,
      "detected_at": "2026-11-02T17:43:22.029Z"
      }
  
   ```
   Click Send in Postman.

8. Check that n8n follows **Webhook → IF True → HTTP Request**. 

9. Check FastAPI terminal for **[INCIDENT] Created incident**.
   Check the FastAPI terminal for **[COORDINATOR] Starting investigation**.

10. Verify Agent Outputs in the terminal. 
Check the A2A logs for investigation, HTN plan generation, and the automatic HITL request and use the following search texts to locate each stage:
   - Monitoring Agent: Search for **[monitor_agent]** to view the monitoring investigation results.
   - Knowledge Agent (RAG): Search for **[knowledge_agent]** to view retrieved historical incidents and runbooks.
   - Summary Agent: Search for **[summary_agent]** to view the generated investigation summary.
   - Remediation Agent (HTN): Search for **plan_id** to find the generated remediation plan and recommended actions.
   - HITL Approval: Search for **[HITL] Approval workflow** to confirm the automatic approval request was initiated.

11. Verify HITL Approval
   - Check the FastAPI terminal for **AWAITING_APPROVAL**. 
   - Open <http://localhost:8000/approval>, enter the incident ID from the HITL logs.
   - Click Approve Remediation or Reject Remediation.
   - Verify that approved remediation is simulated. Search for ** [HITL] Remediation completed**


## HITL approval behavior

- Coordinator-generated recommendation triggers `POST /api/incidents/{incident_id}/request-approval`.
- LangGraph calls `interrupt()` and pauses with `AWAITING_APPROVAL`.
- The HTML page submits `POST /api/incidents/{incident_id}/decision` with `approved` and optional `comments`.
- **Approved:** known rollback/restart actions run through a **simulation-only** execution service.
- **Rejected:** no remediation runs.

For a reliable demo, keep the FastAPI process running between the approval request and decision.


## Project status and limitations

This project is a local demonstration of a multi-agent incident response system using MCP, RAG, HTN planning, and human approval. Remediation actions are simulated, not performed on real systems.

Currently, approval data is lost if FastAPI restarts. To use this system in production, we would need to save workflow data permanently, add user authentication and permissions, validate remediation actions, secure connections, improve logging and monitoring
