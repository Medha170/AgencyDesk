import uuid
from datetime import datetime, date, timezone
from typing import Optional
from sqlalchemy import Text, Integer, Date, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logged_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        ForeignKeyConstraint(["task_id", "agency_id"], ["tasks.id", "tasks.agency_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["membership_id", "agency_id"], ["memberships.id", "memberships.agency_id"], ondelete="CASCADE"),
    )