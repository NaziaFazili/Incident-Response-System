import logging

from fastapi import FastAPI

from app.api.incidents import router as incident_router
from config.logging_config import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Agent Incident Response System")
app.include_router(incident_router)


@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "healthy"}
