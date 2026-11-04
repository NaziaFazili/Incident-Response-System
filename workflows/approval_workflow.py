import json
import logging
from typing import Any, NotRequired, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from services.remediation_execution_service import execute_remediation

logger = logging.getLogger(__name__)


# Data shared between workflow steps
class ApprovalState(TypedDict):
    incident_id: str
    recommended_action: str
    approved: bool
    status: str
    comments: str
    execution_result: NotRequired[dict[str, Any]]


# Step 1: Pause and request human approval
def request_approval(state: ApprovalState):
    logger.info("[HITL]  Requesting remediation approval for: %s", state["incident_id"])

    decision = interrupt(
        {
            "type": "remediation_approval",
            "incident_id": state["incident_id"],
            "recommended_action": state["recommended_action"],
            "message": "Approve executing this remediation?",
        }
    )

    if isinstance(decision, str):
        decision = json.loads(decision)

    approved = decision.get("approved", False)
    comments = decision.get("comments", "")

    decision_status = "APPROVED" if approved else "REJECTED"

    # Record the human decision
    entry = {
        "approved": approved,
        "status": decision_status,
        "comments": comments,
    }

    logger.info(
        "[HITL] Incident %s - Remediation decision Decision: %s",
        state["incident_id"],
        decision_status,
    )

    return {
        "approved": approved,
        "status": decision_status,
        "comments": comments,
    }


# Step 2: Decide which path to follow
def route_after_submission(state: ApprovalState) -> str:

    route = "approved" if state["approved"] else "rejected"

    logger.info("[HITL] Routing to: %s", route)

    return route


# Step 3: Approved path
def approved_action(state: ApprovalState):
    incident_id = state["incident_id"]
    recommended_action = state["recommended_action"]

    result = execute_remediation(
        incident_id,
        recommended_action,
    )

    logger.info(
        "[HITL] Remediation completed for incident %s",
        state["incident_id"],
    )

    return {
        "status": "EXECUTED",
        "execution_result": result,
    }


# Step 4: Rejected path
def rejected_action(state: ApprovalState):
    logger.info("[HITL] Rejected remediation for incident %s", state["incident_id"])

    # No email will be sent
    return {"status": "REJECTED"}


# Step 5: Build the LangGraph workflow
def create_approval_workflow():

    builder = StateGraph(ApprovalState)

    builder.add_node("request_approval", request_approval)
    builder.add_node("approved_action", approved_action)
    builder.add_node("rejected_action", rejected_action)

    builder.add_edge(START, "request_approval")

    builder.add_conditional_edges(
        "request_approval",
        route_after_submission,
        {"approved": "approved_action", "rejected": "rejected_action"},
    )

    builder.add_edge("approved_action", END)
    builder.add_edge("rejected_action", END)

    return builder.compile(checkpointer=MemorySaver())
