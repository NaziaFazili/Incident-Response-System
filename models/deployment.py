from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DeploymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class Deployment(BaseModel):
    deployment_id: str = Field(min_length=1)
    service: str = Field(min_length=1)
    deployed_at: datetime
    status: DeploymentStatus
