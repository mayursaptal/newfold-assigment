"""Pytest configuration and fixtures.

This module provides pytest fixtures for testing the FastAPI application.
It sets up an in-memory SQLite database for testing and provides async
HTTP client fixtures for making API requests.

Fixtures:
    db_session: Async database session with in-memory SQLite database
    client: Async HTTP client for making API requests
    sync_client: Synchronous HTTP client for making API requests

Example:
    ```python
    import pytest

    @pytest.mark.asyncio
    async def test_endpoint(client: AsyncClient):
        response = await client.get("/api/v1/films/")
        assert response.status_code == 200
    ```
"""

import pytest
import sqlite3
from typing import AsyncGenerator
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from fastapi.testclient import TestClient
from app.main import app
from core.dependencies import get_db_session


# Configure SQLite datetime adapters to avoid deprecation warnings
def adapt_datetime_iso(val: datetime) -> str:
    """Adapt datetime to ISO string format."""
    return val.isoformat()


def convert_datetime(val: bytes) -> datetime:
    """Convert ISO string back to datetime."""
    return datetime.fromisoformat(val.decode())


# Register the adapters
sqlite3.register_adapter(type(None), lambda x: None)

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
async def db_session() -> AsyncGenerator[AsyncSession, None]:
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
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with database session override.

    Args:
        db_session: Test database session

    Yields:
        AsyncClient: Test HTTP client
    """
    from httpx import ASGITransport

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    # Use the app directly as ASGI application
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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
