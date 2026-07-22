import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Enum, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class MembershipRole(str, enum.Enum):
    AGENCY_ADMIN = "agency_admin"
    AGENCY_MEMBER = "agency_member"
    CLIENT_USER = "client_user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    memberships: Mapped[List["Membership"]] = relationship("Membership", back_populates="user", cascade="all, delete-orphan")


class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[MembershipRole] = mapped_column(Enum(MembershipRole), nullable=False)
    client_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="memberships")
    agency: Mapped["Agency"] = relationship("Agency", back_populates="memberships")

    __table_args__ = (
        # Ensure client_id belongs to the same agency context
        ForeignKeyConstraint(
            ["client_id", "agency_id"],
            ["clients.id", "clients.agency_id"],
            ondelete="CASCADE",
        ),
        # User can only have one membership record per agency
        UniqueConstraint("user_id", "agency_id", name="uq_user_agency"),
        # Crucial for composite FK references in task assignments and time entries
        UniqueConstraint("id", "agency_id", name="uq_membership_agency"),
    )