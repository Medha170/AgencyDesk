import sys
import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine

# Ensure the root backend directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(autouse=True)
async def cleanup_db_engine():
    """
    Dispose of the global SQLAlchemy engine pool before each test
    so asyncpg doesn't bind connections across different loops.
    """
    await engine.dispose()
    yield
    await engine.dispose()

@pytest.fixture
def agency_a_id():
    return "00000000-0000-0000-0000-000000000001"

@pytest.fixture
def agency_b_id():
    return "00000000-0000-0000-0000-000000000002"

@pytest.fixture
def client_user_token():
    return "mock_client_token_string"

@pytest.fixture
def client_user_headers(client_user_token, agency_a_id):
    return {
        "Authorization": f"Bearer {client_user_token}",
        "X-Agency-ID": str(agency_a_id)
    }

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client