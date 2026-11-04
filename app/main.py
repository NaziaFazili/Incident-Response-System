import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.incidents import router as incident_router
from config.logging_config import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Agent Incident Response System")
app.include_router(incident_router)


@app.get("/approval")
def approval_page():
    file_path = Path(__file__).parent / "static" / "approval.html"
    return FileResponse(file_path)


@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "healthy"}
