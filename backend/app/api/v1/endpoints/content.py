from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.api import deps
from app.models.tenant import Agency
from app.models.project import Task
from app.models.content import TaskFile, TaskComment
from app.models.user import User, Membership
from app.schemas.content import (
    TaskFileCreate, TaskFileResponse, TaskFileStatusUpdate,
    TaskCommentCreate, TaskCommentResponse
)
from app.models.audit import AuditAction
from app.services.audit import log_activity

router = APIRouter()

# ------------------------------------------------------------------
# TASK FILES / DELIVERABLES
# ------------------------------------------------------------------

@router.get("/tasks/{task_id}/files", response_model=List[TaskFileResponse])
async def list_task_files(
    task_id: UUID,
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List all uploaded files/deliverables attached to a specific task.
    """
    query = select(TaskFile).where(
        TaskFile.task_id == task_id,
        TaskFile.agency_id == current_agency.id
    )
    # If the user is a client_user, filter out internal files!
    if getattr(current_user, "role", None) == "client_user":
        query = query.where(TaskFile.is_internal == False)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/tasks/{task_id}/files", response_model=TaskFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_task_file(
    task_id: UUID,
    file_in: TaskFileCreate,
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Attach a new deliverable file or asset reference to a task.
    """
    # 1. Verify task belongs to current agency
    task_res = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.agency_id == current_agency.id
        )
    )
    if not task_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in active agency"
        )

    # 2. Resolve the current user's membership in the active agency
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

    task_file = TaskFile(
        agency_id=current_agency.id,
        task_id=task_id,
        uploaded_by_membership_id=membership.id,
        file_name=file_in.file_name,
        file_url=file_in.file_url,
        is_internal=file_in.is_internal
    )
    db.add(task_file)
    await db.commit()
    await db.refresh(task_file)

    # Log file creation activity after the file has a persisted ID
    await log_activity(
        db=db,
        agency_id=current_agency.id,
        actor_membership_id=membership.id,
        entity_type="file",
        entity_id=task_file.id,
        action=AuditAction.CREATED,
        description=f"Uploaded deliverable '{task_file.file_name}' to task",
        metadata_json={
            "task_id": str(task_id),
            "file_name": task_file.file_name,
            "is_internal": task_file.is_internal
        }
    )

    await db.commit()
    return task_file


@router.patch("/files/{file_id}/status", response_model=TaskFileResponse)
async def update_file_approval_status(
    file_id: UUID,
    status_update: TaskFileStatusUpdate,
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Approve, request changes, or reset approval status on a task deliverable file.
    """
    result = await db.execute(
        select(TaskFile).where(
            TaskFile.id == file_id,
            TaskFile.agency_id == current_agency.id
        )
    )
    task_file = result.scalar_one_or_none()
    if not task_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task file not found"
        )

    previous_status = task_file.approval_status
    task_file.approval_status = status_update.approval_status

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

    # Log status change activity
    await log_activity(
        db=db,
        agency_id=current_agency.id,
        actor_membership_id=membership.id,
        entity_type="file",
        entity_id=task_file.id,
        action=AuditAction.STATUS_CHANGED,
        description=f"Changed status of '{task_file.file_name}' from {previous_status} to {status_update.approval_status.value}",
        metadata_json={
            "task_id": str(task_file.task_id),
            "old_status": previous_status,
            "new_status": status_update.approval_status.value
        }
    )

    await db.commit()
    await db.refresh(task_file)
    return task_file


# ------------------------------------------------------------------
# TASK COMMENTS
# ------------------------------------------------------------------

@router.get("/tasks/{task_id}/comments", response_model=List[TaskCommentResponse])
async def list_task_comments(
    task_id: UUID,
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List all comments on a task scoped to the active agency.
    """
    query = select(TaskComment).where(
        TaskComment.task_id == task_id,
        TaskComment.agency_id == current_agency.id
    )
    # If the user is a client_user, filter out internal comments!
    if getattr(current_user, "role", None) == "client_user":
        query = query.where(TaskComment.is_internal == False)

    result = await db.execute(query.order_by(TaskComment.created_at.asc()))
    return result.scalars().all()


@router.post("/tasks/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_task_comment(
    task_id: UUID,
    comment_in: TaskCommentCreate,
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Add a comment to a task (supports internal team notes vs. public client comments).
    """
    task_res = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.agency_id == current_agency.id
        )
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

    comment = TaskComment(
        agency_id=current_agency.id,
        task_id=task_id,
        author_membership_id=membership.id,
        content=comment_in.content,
        is_internal=comment_in.is_internal
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    # Log comment activity after the comment has a persisted ID
    comment_type = "internal comment" if comment_in.is_internal else "comment"
    await log_activity(
        db=db,
        agency_id=current_agency.id,
        actor_membership_id=membership.id,
        entity_type="comment",
        entity_id=comment.id,
        action=AuditAction.CREATED,
        description=f"Posted a {comment_type} on task",
        metadata_json={
            "task_id": str(task_id),
            "is_internal": comment_in.is_internal
        }
    )

    await db.commit()
    return comment