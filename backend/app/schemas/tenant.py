from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ClientBase(BaseModel):
    name: str

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: UUID
    agency_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class AgencyResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True