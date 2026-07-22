import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Agency(Base):
    __tablename__ = "agencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    memberships: Mapped[List["Membership"]] = relationship("Membership", back_populates="agency", cascade="all, delete-orphan")
    clients: Mapped[List["Client"]] = relationship("Client", back_populates="agency", cascade="all, delete-orphan")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    agency: Mapped["Agency"] = relationship("Agency", back_populates="clients")

    __table_args__ = (
        # Required to anchor downstream composite FKs
        UniqueConstraint("id", "agency_id", name="uq_client_agency"),
    )