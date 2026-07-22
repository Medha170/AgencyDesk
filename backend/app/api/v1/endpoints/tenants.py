from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.api import deps
from app.models.tenant import Agency, Client
from app.models.user import User
from app.schemas.tenant import AgencyResponse, ClientResponse, ClientCreate

router = APIRouter()

@router.get("/agencies", response_model=List[AgencyResponse])
async def list_agencies(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List all agencies in the platform.
    """
    result = await db.execute(select(Agency))
    return result.scalars().all()

@router.get("/clients", response_model=List[ClientResponse])
async def list_agency_clients(
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List all clients under the active tenant agency (resolved via X-Agency-ID).
    """
    result = await db.execute(
        select(Client).where(Client.agency_id == current_agency.id)
    )
    return result.scalars().all()

@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_in: ClientCreate,
    current_agency: Agency = Depends(deps.get_current_agency),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new client for the active tenant agency.
    """
    client = Client(
        name=client_in.name,
        agency_id=current_agency.id
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client