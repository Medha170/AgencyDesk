import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.user import User, Membership, MembershipRole
from app.models.tenant import Agency, Client
from app.models.project import Project, Task, TaskStatus, TaskPriority
from app.models.content import TaskComment, TaskFile, ApprovalStatus
from app.models.tracking import TimeEntry

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def seed_data():
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding database...")

        # ---------------------------------------------------------------------
        # 1. AGENCIES
        # ---------------------------------------------------------------------
        agency_a = Agency(name="Apex Digital Marketing")
        agency_b = Agency(name="ByteCraft Software")
        db.add_all([agency_a, agency_b])
        await db.flush()

        # ---------------------------------------------------------------------
        # 2. CLIENTS
        # ---------------------------------------------------------------------
        client_a1 = Client(agency_id=agency_a.id, name="Acme Corp")
        client_b1 = Client(agency_id=agency_b.id, name="Starlight Retail")
        db.add_all([client_a1, client_b1])
        await db.flush()

        # ---------------------------------------------------------------------
        # 3. USERS & MEMBERSHIPS (Testing "One person, two agencies")
        # ---------------------------------------------------------------------
        hashed_pw = get_password_hash("password123")

        # Global identities
        admin_user = User(email="admin@apexdigital.com", password_hash=hashed_pw, full_name="Alice Admin")
        member_user = User(email="dev@apexdigital.com", password_hash=hashed_pw, full_name="Bob Developer")
        client_user = User(email="charlie@acme.com", password_hash=hashed_pw, full_name="Charlie Client")
        
        # Dual-agency user (Client in Agency A, Member in Agency B)
        dual_user = User(email="dual.user@gmail.com", password_hash=hashed_pw, full_name="Diana Dual")

        db.add_all([admin_user, member_user, client_user, dual_user])
        await db.flush()

        # Memberships
        m_admin_a = Membership(user_id=admin_user.id, agency_id=agency_a.id, role=MembershipRole.AGENCY_ADMIN)
        m_member_a = Membership(user_id=member_user.id, agency_id=agency_a.id, role=MembershipRole.AGENCY_MEMBER)
        m_client_a = Membership(user_id=client_user.id, agency_id=agency_a.id, role=MembershipRole.CLIENT_USER, client_id=client_a1.id)

        # Dual user memberships across tenants
        m_dual_client_a = Membership(user_id=dual_user.id, agency_id=agency_a.id, role=MembershipRole.CLIENT_USER, client_id=client_a1.id)
        m_dual_member_b = Membership(user_id=dual_user.id, agency_id=agency_b.id, role=MembershipRole.AGENCY_MEMBER)

        db.add_all([m_admin_a, m_member_a, m_client_a, m_dual_client_a, m_dual_member_b])
        await db.flush()

        # ---------------------------------------------------------------------
        # 4. PROJECTS & TASKS
        # ---------------------------------------------------------------------
        project_a1 = Project(agency_id=agency_a.id, client_id=client_a1.id, name="Acme Rebrand & Website", description="Full brand design and portal")
        db.add(project_a1)
        await db.flush()

        # Client-visible Task
        task_public = Task(
            agency_id=agency_a.id,
            project_id=project_a1.id,
            assignee_membership_id=m_member_a.id,
            title="Design Homepage Wireframes",
            description="Create initial layout concept for review",
            status=TaskStatus.IN_REVIEW,
            priority=TaskPriority.HIGH,
            due_date=datetime.now(timezone.utc) + timedelta(days=5),
            is_internal=False  # Visible to Charlie Client
        )

        # Internal Agency-only Task
        task_internal = Task(
            agency_id=agency_a.id,
            project_id=project_a1.id,
            assignee_membership_id=m_member_a.id,
            title="Internal Rate Calculation & Margin Audit",
            description="Discuss pricing markup with admin",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.URGENT,
            due_date=datetime.now(timezone.utc) + timedelta(days=2),
            is_internal=True  # MUST BE HIDDEN from client
        )

        db.add_all([task_public, task_internal])
        await db.flush()

        # ---------------------------------------------------------------------
        # 5. TIME ENTRIES, FILES & COMMENTS
        # ---------------------------------------------------------------------
        time_1 = TimeEntry(
            agency_id=agency_a.id,
            task_id=task_public.id,
            membership_id=m_member_a.id,
            duration_minutes=120,
            note="Worked on Figma component designs"
        )

        file_1 = TaskFile(
            agency_id=agency_a.id,
            task_id=task_public.id,
            uploaded_by_membership_id=m_member_a.id,
            file_name="homepage_wireframe_v1.pdf",
            file_url="https://s3.amazonaws.com/bucket/homepage_v1.pdf",
            is_internal=False,
            approval_status=ApprovalStatus.PENDING
        )

        comment_public = TaskComment(
            agency_id=agency_a.id,
            task_id=task_public.id,
            author_membership_id=m_client_a.id,
            content="Looking great! Can we make the hero banner larger?",
            is_internal=False
        )

        comment_internal = TaskComment(
            agency_id=agency_a.id,
            task_id=task_internal.id,
            author_membership_id=m_admin_a.id,
            content="Margin target is 35% minimum.",
            is_internal=True
        )

        db.add_all([time_1, file_1, comment_public, comment_internal])
        await db.commit()
        print("✅ Database successfully seeded!")

if __name__ == "__main__":
    asyncio.run(seed_data())