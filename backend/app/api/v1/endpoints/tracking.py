from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.api import deps
from app.models.tenant import Agency
from app.models.project import Task, Project
from app.models.tracking import TimeEntry
from app.models.user import User, Membership
from app.schemas.tracking import TimeEntryCreate, TimeEntryResponse, ProjectHoursSummaryResponse

router = APIRouter()

@router.post("/tasks/{task_id}/time", response_model=TimeEntryResponse, status_code=status.HTTP_201_CREATED)
async def log_time_entry(
    task_id: UUID,
    time_in: TimeEntryCreate,
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Agency members log time spent on a task.
    """
    # 1. Block client_user from logging time
    user_role = getattr(current_user, "role", "agency_member")
    if user_role == "client_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client users cannot log time entries."
        )

    # 2. Verify task belongs to current agency
    task_res = await db.execute(
        select(Task).where(Task.id == task_id, Task.agency_id == current_agency.id)
    )
    if not task_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in active agency"
        )

    membership_res = await db.execute(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.agency_id == current_agency.id,
        )
    )
    membership = membership_res.scalar_one_or_none()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of the current agency"
        )

    entry = TimeEntry(
        agency_id=current_agency.id,
        task_id=task_id,
        membership_id=membership.id,
        duration_minutes=time_in.duration_minutes,
        note=time_in.note,
        logged_date=time_in.logged_date
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/projects/{project_id}/hours", response_model=ProjectHoursSummaryResponse)
async def get_project_hours_summary(
    project_id: UUID,
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get aggregated per-project logged hours summary.
    """
    # Verify project belongs to agency
    proj_res = await db.execute(
        select(Project).where(Project.id == project_id, Project.agency_id == current_agency.id)
    )
    if not proj_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    # Aggregate total minutes across tasks in project
    res = await db.execute(
        select(func.coalesce(func.sum(TimeEntry.duration_minutes), 0))
        .join(Task, Task.id == TimeEntry.task_id)
        .where(Task.project_id == project_id, TimeEntry.agency_id == current_agency.id)
    )
    total_minutes = res.scalar() or 0

    return ProjectHoursSummaryResponse(
        project_id=project_id,
        total_duration_minutes=total_minutes,
        total_hours=round(total_minutes / 60.0, 2)
    )