"""Tests for category endpoints - one happy-path test per endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_categories(client: AsyncClient):
    """Happy-path: Get all categories with pagination."""
    response = await client.get("/api/v1/categories?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_category_by_id(client: AsyncClient):
    """Happy-path: Get category by ID."""
    # First get categories to find a valid ID
    categories_response = await client.get("/api/v1/categories?skip=0&limit=1")
    if categories_response.status_code == 200 and categories_response.json():
        category_id = categories_response.json()[0]["id"]
        response = await client.get(f"/api/v1/categories/{category_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert "name" in data
    else:
        # If no categories exist, skip this test or create one
        pytest.skip("No categories available in test database")

