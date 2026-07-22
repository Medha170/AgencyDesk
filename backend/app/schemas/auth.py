from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID

# Token Response Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# Membership & User Response Schemas
class MembershipResponse(BaseModel):
    id: UUID
    agency_id: UUID
    role: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    memberships: List[MembershipResponse] = []

    class Config:
        from_attributes = True