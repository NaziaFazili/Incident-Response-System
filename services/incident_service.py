from uuid import uuid4

from models.incident import (
    Incident,
    IncidentAlertRequest,
    IncidentStatus,
)


class IncidentService:
    def __init__(self):
        self.incidents: dict[str, Incident] = {}

    def create_incident(self, alert: IncidentAlertRequest) -> Incident:
        """Create a new incident from an n8n alert."""

        incident_id = f"INC-{uuid4().hex[:8].upper()}"

        incident = Incident(
            incident_id=incident_id,
            service=alert.service,
            alert_type=alert.alert_type,
            severity=alert.severity,
            detail=alert.detail,
            detected_at=alert.detected_at,
            status=IncidentStatus.OPEN,
        )

        self.incidents[incident.incident_id] = incident

        return incident

    def get_incident(self, incident_id: str) -> Incident | None:
        """Retrieve an incident by its ID."""
        return self.incidents.get(incident_id)
