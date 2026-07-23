from fastapi import APIRouter
from app.api.v1.endpoints import auth, tenants, projects, content, analytics, tracking

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants & Clients"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects & Tasks"])
api_router.include_router(content.router, prefix="/content", tags=["Deliverables & Comments"])
api_router.include_router(tracking.router, prefix="/tracking", tags=["Time Tracking"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics, Search & Activity"])