import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Enum, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    NEEDS_CHANGES = "needs_changes"


class TaskFile(Base):
    __tablename__ = "task_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    uploaded_by_membership_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approval_status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        ForeignKeyConstraint(["task_id", "agency_id"], ["tasks.id", "tasks.agency_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["uploaded_by_membership_id", "agency_id"], ["memberships.id", "memberships.agency_id"], ondelete="CASCADE"),
    )


class TaskComment(Base):
    __tablename__ = "task_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    author_membership_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        ForeignKeyConstraint(["task_id", "agency_id"], ["tasks.id", "tasks.agency_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["author_membership_id", "agency_id"], ["memberships.id", "memberships.agency_id"], ondelete="CASCADE"),
    )