"""Happy-path tests for category endpoints.

This module contains one happy-path test per category endpoint.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_categories(client: AsyncClient) -> None:
    """Happy-path: Get all categories with pagination."""
    response = await client.get("/api/v1/categories?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_category_by_id(client: AsyncClient, db_session: AsyncSession) -> None:
    """Happy-path: Get category by ID."""
    # Create a category directly in the database for testing
    from domain.models.category import Category
    from datetime import datetime

    category = Category(name="Test Category", last_update=datetime.now())
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    category_id = category.id

    # Then get it by ID via API
    response = await client.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Test Category"
