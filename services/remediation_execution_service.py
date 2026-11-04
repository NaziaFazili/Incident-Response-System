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

    action_lower = action.lower()

    if "rollback" in action_lower:
        action_type = "rollback_deployment"
    elif "restart" in action_lower:
        action_type = "restart_service"
    else:
        raise ValueError(f"Unsupported remediation action: {action}")

    logger.info(
        "[REMEDIATION] Simulating %s for incident %s",
        action_type,
        incident_id,
    )

    return {
        "incident_id": incident_id,
        "action": action_type,
        "original_action": action,
        "status": "SUCCESS",
        "message": f"Simulated {action_type} completed successfully.",
    }
