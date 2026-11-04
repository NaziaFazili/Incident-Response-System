import logging

from config.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

ALLOWED_ACTIONS = {
    "rollback_to_dep_1001": "rollback_deployment",
    "rollback_deployment": "rollback_deployment",
    "restart_service": "restart_service",
}


def execute_remediation(incident_id: str, action: str) -> dict:
    """Simulate a remediation action after human approval."""

    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Unsupported remediation action: {action}")

    action = ALLOWED_ACTIONS[action]
    logger.info(
        "[REMEDIATION] Simulating %s for incident %s",
        action,
        incident_id,
    )

    return {
        "incident_id": incident_id,
        "action": action,
        "status": "SUCCESS",
        "message": f"Simulated {action} completed successfully.",
    }
