import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from config.logging_config import configure_logging
from models.incident import Incident, IncidentAlertRequest
from services.approval_service import request_approval, submit_decision
from services.coordinator_trigger_service import trigger_coordinator
from services.incident_service import IncidentService

configure_logging()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

incident_service = IncidentService()


@router.post("", response_model=Incident, status_code=201)
def create_incident(alert: IncidentAlertRequest, background_tasks: BackgroundTasks):
    """Receive an incident alert from n8n."""

    incident = incident_service.create_incident(alert)

    logger.info("[INCIDENT] Created incident: %s", incident.incident_id)

    background_tasks.add_task(
        trigger_coordinator,
        incident.model_dump(mode="json"),
    )

    logger.info("[INCIDENT] Coordinator task scheduled")

    return incident


@router.get("/{incident_id}", response_model=Incident)
def get_incident(incident_id: str):
    """Retrieve an incident by ID."""

    incident = incident_service.get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


# -------------------- End points for Approval for LangGraph interrupt
class ApprovalRequest(BaseModel):
    recommended_action: str


class ApprovalDecisionRequest(BaseModel):
    approved: bool
    comments: str = ""


# Start the LangGraph HITL approval workflow
@router.post("/{incident_id}/request-approval")
def start_approval(incident_id: str, request: ApprovalRequest):
    try:
        return request_approval(
            incident_id,
            request.recommended_action,
        )
    except Exception as ex:
        logger.exception(
            "[HITL] Error requesting remediation approval for %s",
            incident_id,
        )
    raise HTTPException(
        status_code=500,
        detail="Failed to start remediation approval workflow.",
    )


# Approve or reject the proposed remediation
@router.post("/{incident_id}/decision")
def decide_approval(incident_id: str, request: ApprovalDecisionRequest):
    try:
        return submit_decision(incident_id, request.approved, request.comments)
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
