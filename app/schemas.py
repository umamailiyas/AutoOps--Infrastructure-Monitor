from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ServiceCreate(BaseModel):
    name: str

class ServiceResponse(BaseModel):
    id: int
    name: str
    status: str
    last_checked: datetime

    class Config:
        from_attributes = True

class HealthCheckIn(BaseModel):
    service_name: str
    status: str  # "healthy" or "unhealthy"
    issue: Optional[str] = None

class IncidentResponse(BaseModel):
    id: int
    service_name: str
    issue: str
    action_taken: str
    created_at: datetime

    class Config:
        from_attributes = True