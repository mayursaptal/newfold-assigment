"""Happy-path tests for category endpoints.

This module contains one happy-path test per category endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_categories(client: AsyncClient):
    """Happy-path: Get all categories with pagination."""
    response = await client.get("/api/v1/categories?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_category_by_id(client: AsyncClient):
    """Happy-path: Get category by ID."""
    # First get all categories to find an existing ID
    categories_response = await client.get("/api/v1/categories?skip=0&limit=1")
    if categories_response.status_code == 200 and categories_response.json():
        category_id = categories_response.json()[0]["id"]
        
        # Then get it by ID
        response = await client.get(f"/api/v1/categories/{category_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id

