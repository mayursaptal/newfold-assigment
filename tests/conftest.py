"""Pytest configuration and fixtures."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from fastapi.testclient import TestClient
from app.main import app
from core.db import get_async_session
from core.dependencies import get_db_session
from core.settings import settings


# Test database URL (use in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture
async def db_session() -> AsyncSession:
    """
    Create a test database session.
    
    Yields:
        AsyncSession: Test database session
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """
    Create a test client with database session override.
    
    Args:
        db_session: Test database session
        
    Yields:
        AsyncClient: Test HTTP client
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sync_client() -> TestClient:
    """
    Create a synchronous test client.
    
    Yields:
        TestClient: Synchronous test client
    """
    return TestClient(app)

