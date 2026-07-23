from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.api import deps
from app.models.tenant import Agency, Client
from app.models.project import Project, Task
from app.models.user import User
from app.schemas.project import ProjectResponse, ProjectCreate, TaskResponse, TaskCreate

router = APIRouter()

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retrieve all projects belonging to the active tenant agency.
    """
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.tasks))
        .where(Project.agency_id == current_agency.id)
    )
    return result.scalars().all()

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new project linked to a client under the active tenant agency.
    """
    # Check that client exists and belongs to this agency
    client_res = await db.execute(
        select(Client).where(
            Client.id == project_in.client_id, 
            Client.agency_id == current_agency.id
        )
    )
    if not client_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found in current agency"
        )

    project = Project(
        name=project_in.name,
        description=project_in.description,
        client_id=project_in.client_id,
        agency_id=current_agency.id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    result = await db.execute(
        select(Project)
        .options(selectinload(Project.tasks))
        .where(Project.id == project.id)
    )
    return result.scalar_one()

@router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_for_project(
    project_id: UUID,
    task_in: TaskCreate,
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Add a task to a project scoped to the current tenant agency.
    """
    proj_res = await db.execute(
        select(Project).where(
            Project.id == project_id, 
            Project.agency_id == current_agency.id
        )
    )
    if not proj_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in current agency"
        )

    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        project_id=project_id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task