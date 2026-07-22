from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: UUID
    project_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    client_id: UUID

class ProjectResponse(ProjectBase):
    id: UUID
    agency_id: UUID
    client_id: UUID
    created_at: datetime
    tasks: List[TaskResponse] = []

    class Config:
        from_attributes = True