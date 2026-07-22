from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Engine connecting Python to PostgreSQL
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Factory for creating async database sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

# Dependency injection for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session