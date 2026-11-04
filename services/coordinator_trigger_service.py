import json
import logging
import uuid

import httpx

from config.agents_config import COORDINATOR_AGENT_URL

logger = logging.getLogger(__name__)

# COORDINATOR_URL = "http://127.0.0.1:10022/"


async def trigger_coordinator(incident: dict):
    """Automatically start Coordinator investigation for a new incident."""

    incident_id = incident.get("incident_id") or incident.get("id")

    logger.info(
        "[COORDINATOR] Starting investigation for incident %s",
        incident_id,
    )

    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "messageId": str(uuid.uuid4()),
                "parts": [
                    {
                        "kind": "text",
                        "text": (
                            f"Investigate this incident and generate a remediation plan:\n"
                            f"{json.dumps(incident, indent=2)}"
                        ),
                    }
                ],
            }
        },
    }

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                COORDINATOR_AGENT_URL,
                json=payload,
            )

            response.raise_for_status()

            result = response.json()

            if "error" in result:
                raise RuntimeError(result["error"])

            logger.info(
                "[COORDINATOR] Investigation request completed for %s",
                incident_id,
            )

    except Exception:
        logger.exception(
            "[COORDINATOR] Failed to investigate incident %s",
            incident_id,
        )
