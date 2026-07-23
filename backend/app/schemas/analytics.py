from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID

# --- Analytics Schemas ---
class TaskMetrics(BaseModel):
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int

class FileApprovalMetrics(BaseModel):
    total_files: int
    pending_approval: int
    approved: int
    needs_changes: int

class DashboardOverviewResponse(BaseModel):
    agency_id: UUID
    total_clients: int
    total_projects: int
    active_projects: int
    tasks: TaskMetrics
    deliverables: FileApprovalMetrics


# --- Search Schemas ---
class SearchItem(BaseModel):
    id: UUID
    entity_type: str  # "project", "task", or "client"
    title: str
    subtitle: Optional[str] = None
    status: Optional[str] = None

class SearchResultsResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchItem]


# --- Activity Log Schemas ---
class ActivityLogResponse(BaseModel):
    id: UUID
    agency_id: UUID
    actor_membership_id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    description: str
    metadata_json: Optional[Dict]
    created_at: datetime

    class Config:
        from_attributes = True