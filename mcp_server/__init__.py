from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class IncidentStatus(str, Enum):
    """Represents the current status of an incident.
    - OPEN: Incident has been reported and awaits investigation.
    - INVESTIGATING: The team is actively investigating the issue.
    - AWAITING_APPROVAL: A proposed resolution or action requires approval.
    - RESOLVED: The incident has been fixed or otherwise resolved.
    """

    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    RESOLVED = "RESOLVED"


class Severity(str, Enum):
    """Incident severity levels, from most critical to least critical.
    - CRITICAL: Major outage; immediate action required
    - HIGH: Significant impact; urgent investigation needed
    - MEDIUM: Limited impact; resolve as soon as practical
    - LOW: Minor issue; handle during normal operations
    """

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class IncidentAlertRequest(BaseModel):
    """Represents an incoming alert requesting incident creation.

    - service: Name of the service experiencing the issue.
    - alert_type: Category or type of the incident.
    - severity: Severity level of the incident; defaults to MEDIUM.
    - detail: Description of the issue or observed behavior.
    - detected_at: Date and time when the incident was detected.
    """

    service: str = Field(min_length=1)
    alert_type: str = Field(min_length=1)
    severity: Severity = Severity.MEDIUM
    detail: str = Field(min_length=1)
    detected_at: datetime


class Incident(BaseModel):
    """Represents an incident tracked by the Incident Response system.

    - incident_id: Unique identifier assigned to the incident.
    - service: Name of the service experiencing the issue.
    - alert_type: Category or type of the incident.
    - severity: Severity level of the incident; defaults to MEDIUM.
    - detail: Description of the issue or observed behavior.
    - detected_at: Date and time when the incident was detected.
    - status: Current incident status; defaults to OPEN.
    """

    incident_id: str
    service: str = Field(min_length=1)
    alert_type: str = Field(min_length=1)
    severity: Severity = Severity.MEDIUM
    detail: str = Field(min_length=1)
    detected_at: datetime
    status: IncidentStatus = IncidentStatus.OPEN
