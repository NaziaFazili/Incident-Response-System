from datetime import datetime

from pydantic import BaseModel, Field


class Metric(BaseModel):
    """Represents basic performance measurements for a service.

    Attributes:
        timestamp: Date and time when the metrics were recorded.
        service: Name of the application or service being monitored.
        error_rate_pct: Percentage of requests that resulted in errors (0–100).
        response_time_ms: Service response time in milliseconds; must be non-negative.
    """

    timestamp: datetime
    service: str = Field(min_length=1)
    error_rate_pct: float = Field(ge=0, le=100)
    response_time_ms: float = Field(ge=0)
