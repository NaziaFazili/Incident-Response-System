from fastapi import APIRouter, HTTPException

from models.incident import Incident, IncidentAlertRequest
from services.incident_service import IncidentService

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

incident_service = IncidentService()


@router.post("", response_model=Incident, status_code=201)
def create_incident(alert: IncidentAlertRequest):
    """Receive an incident alert from n8n."""

    return incident_service.create_incident(alert)


@router.get("/{incident_id}", response_model=Incident)
def get_incident(incident_id: str):
    """Retrieve an incident by ID."""

    incident = incident_service.get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident
