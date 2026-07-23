from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from uuid import UUID

class TimeEntryCreate(BaseModel):
    duration_minutes: int = Field(..., gt=0, description="Duration in minutes, must be > 0")
    note: Optional[str] = None
    logged_date: date = Field(default_factory=date.today)

class TimeEntryResponse(BaseModel):
    id: UUID
    agency_id: UUID
    task_id: UUID
    membership_id: UUID
    duration_minutes: int
    note: Optional[str]
    logged_date: date
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectHoursSummaryResponse(BaseModel):
    project_id: UUID
    total_duration_minutes: int
    total_hours: float