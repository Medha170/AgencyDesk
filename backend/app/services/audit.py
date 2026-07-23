from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.audit import ActivityLog, AuditAction

async def log_activity(
    db: AsyncSession,
    agency_id: UUID,
    actor_membership_id: UUID,
    entity_type: str,
    entity_id: UUID,
    action: AuditAction,
    description: str,
    metadata_json: dict = None
):
    log_entry = ActivityLog(
        agency_id=agency_id,
        actor_membership_id=actor_membership_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        description=description,
        metadata_json=metadata_json or {}
    )
    db.add(log_entry)