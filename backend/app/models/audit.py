import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class AuditAction(str, enum.Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    STATUS_CHANGED = "status_changed"


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    actor_membership_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "task", "file", "comment"
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))