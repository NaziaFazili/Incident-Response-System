from enum import Enum

from pydantic import BaseModel, Field


class AgentTaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentTask(BaseModel):
    task_id: str
    incident_id: str
    agent_name: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    status: AgentTaskStatus = AgentTaskStatus.PENDING
