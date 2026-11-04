import logging

from langgraph.types import Command

from config.logging_config import configure_logging
from workflows.approval_workflow import create_approval_workflow

configure_logging()
logger = logging.getLogger(__name__)
# Create once so approval state is preserved between API requests
workflow = create_approval_workflow()


def request_approval(
    incident_id: str,
    recommended_action: str,
):
    config = {"configurable": {"thread_id": incident_id}}

    logger.info("[HITL] Starting approval workflow for %s", incident_id)
    result = workflow.invoke(
        {
            "incident_id": incident_id,
            "recommended_action": recommended_action,
            "approved": False,
            "status": "AWAITING_APPROVAL",
            "comments": "",
        },
        config=config,
    )
    logger.info("[HITL] Workflow result: %s", result)
    if not result.get("__interrupt__"):
        raise RuntimeError("Approval workflow did not pause.")

    return {
        "incident_id": incident_id,
        "status": "AWAITING_APPROVAL",
        "recommended_action": recommended_action,
    }


def submit_decision(incident_id: str, approved: bool, comments: str):
    """Resume the workflow with the human decision."""

    config = {"configurable": {"thread_id": incident_id}}

    # Ensure this incident is actually awaiting approval
    snapshot = workflow.get_state(config)
    if not snapshot.next or "request_approval" not in snapshot.next:
        raise ValueError("No pending email approval for this incident.")

    result = workflow.invoke(
        Command(resume={"approved": approved, "comments": comments}),
        config=config,
    )

    return {
        "incident_id": incident_id,
        "approved": result["approved"],
        "status": result["status"],
        "comments": result["comments"],
    }
