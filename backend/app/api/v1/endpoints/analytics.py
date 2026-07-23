from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from uuid import UUID

from app.api import deps
from app.models.tenant import Agency, Client
from app.models.project import Project, Task, TaskStatus
from app.models.content import TaskFile, ApprovalStatus
from app.models.audit import ActivityLog, AuditAction
from app.models.user import User
from app.schemas.analytics import (
    DashboardOverviewResponse, TaskMetrics, FileApprovalMetrics,
    SearchResultsResponse, SearchItem, ActivityLogResponse
)

router = APIRouter()


# ------------------------------------------------------------------
# 1. DASHBOARD OVERVIEW ANALYTICS
# ------------------------------------------------------------------

@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get aggregated tenant metrics: active projects, task completion status,
    and deliverable approval counts.
    """
    agency_id = current_agency.id

    # Count Clients
    client_count_res = await db.execute(
        select(func.count(Client.id)).where(Client.agency_id == agency_id)
    )
    total_clients = client_count_res.scalar() or 0

    # Count Projects
    project_count_res = await db.execute(
        select(func.count(Project.id)).where(Project.agency_id == agency_id)
    )
    total_projects = project_count_res.scalar() or 0
    active_projects = total_projects

    # Count Tasks by status
    task_stats_res = await db.execute(
        select(
            func.count(Task.id),
            func.count(func.nullif(Task.status == TaskStatus.TODO, False)),
            func.count(func.nullif(Task.status == TaskStatus.IN_PROGRESS, False)),
            func.count(func.nullif(Task.status == TaskStatus.COMPLETED, False))
        ).where(Task.agency_id == agency_id)
    )
    total_tasks, todo_tasks, in_prog_tasks, completed_tasks = task_stats_res.one()

    # Count Deliverable Files by approval status
    file_stats_res = await db.execute(
        select(
            func.count(TaskFile.id),
            func.count(func.nullif(TaskFile.approval_status == ApprovalStatus.PENDING, False)),
            func.count(func.nullif(TaskFile.approval_status == ApprovalStatus.APPROVED, False)),
            func.count(func.nullif(TaskFile.approval_status == ApprovalStatus.NEEDS_CHANGES, False))
        ).where(TaskFile.agency_id == agency_id)
    )
    total_files, pending_files, approved_files, needs_change_files = file_stats_res.one()

    return DashboardOverviewResponse(
        agency_id=agency_id,
        total_clients=total_clients,
        total_projects=total_projects,
        active_projects=active_projects or 0,
        tasks=TaskMetrics(
            total_tasks=total_tasks or 0,
            pending_tasks=todo_tasks or 0,
            in_progress_tasks=in_prog_tasks or 0,
            completed_tasks=completed_tasks or 0
        ),
        deliverables=FileApprovalMetrics(
            total_files=total_files or 0,
            pending_approval=pending_files or 0,
            approved=approved_files or 0,
            needs_changes=needs_change_files or 0
        )
    )


# ------------------------------------------------------------------
# 2. GLOBAL TENANT SEARCH
# ------------------------------------------------------------------

@router.get("/search", response_model=SearchResultsResponse)
async def global_tenant_search(
    q: str = Query(..., min_length=2, description="Search term"),
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Search across projects, tasks, and clients within the active agency.
    """
    search_pattern = f"%{q}%"
    results: List[SearchItem] = []

    # Search Projects
    projects_res = await db.execute(
        select(Project).where(
            Project.agency_id == current_agency.id,
            or_(
                Project.name.ilike(search_pattern),
                Project.description.ilike(search_pattern)
            )
        ).limit(10)
    )
    for p in projects_res.scalars().all():
        results.append(SearchItem(
            id=p.id,
            entity_type="project",
            title=p.name,
            subtitle=p.description[:60] if p.description else None,
            status=getattr(p, "status", None)
        ))

    # Search Tasks
    tasks_res = await db.execute(
        select(Task).where(
            Task.agency_id == current_agency.id,
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        ).limit(10)
    )
    for t in tasks_res.scalars().all():
        results.append(SearchItem(
            id=t.id,
            entity_type="task",
            title=t.title,
            subtitle=t.description[:60] if t.description else None,
            status=getattr(t, "status", None)
        ))

    # Search Clients
    clients_res = await db.execute(
        select(Client).where(
            Client.agency_id == current_agency.id,
            Client.name.ilike(search_pattern)
        ).limit(10)
    )
    for c in clients_res.scalars().all():
        results.append(SearchItem(
            id=c.id,
            entity_type="client",
            title=c.name,
            subtitle=getattr(c, "company_name", None),
            status="active"
        ))

    return SearchResultsResponse(
        query=q,
        total_results=len(results),
        results=results
    )


# ------------------------------------------------------------------
# 3. ACTIVITY FEED & AUDIT LOGS
# ------------------------------------------------------------------

@router.get("/activity", response_model=List[ActivityLogResponse])
async def get_activity_feed(
    limit: int = Query(20, ge=1, le=100),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (e.g. task, file)"),
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get recent agency activity and audit logs.
    """
    query = select(ActivityLog).where(ActivityLog.agency_id == current_agency.id)

    if entity_type:
        query = query.where(ActivityLog.entity_type == entity_type)

    query = query.order_by(ActivityLog.created_at.desc()).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()