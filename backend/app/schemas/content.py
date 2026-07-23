from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    NEEDS_CHANGES = "needs_changes"

# --- Task File Schemas ---
class TaskFileCreate(BaseModel):
    file_name: str
    file_url: str
    is_internal: bool = False

class TaskFileStatusUpdate(BaseModel):
    approval_status: ApprovalStatus

class TaskFileResponse(BaseModel):
    id: UUID
    agency_id: UUID
    task_id: UUID
    uploaded_by_membership_id: UUID
    file_name: str
    file_url: str
    is_internal: bool
    approval_status: ApprovalStatus
    created_at: datetime

    class Config:
        from_attributes = True


# --- Task Comment Schemas ---
class TaskCommentCreate(BaseModel):
    content: str
    is_internal: bool = False

class TaskCommentResponse(BaseModel):
    id: UUID
    agency_id: UUID
    task_id: UUID
    author_membership_id: UUID
    content: str
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True