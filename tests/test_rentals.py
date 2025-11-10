"""Happy-path tests for rental endpoints.

This module contains one happy-path test per rental endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_rental(client: AsyncClient):
    """Happy-path: Create a new rental."""
    rental_data = {"inventory_id": 1, "customer_id": 1, "staff_id": 1}
    response = await client.post("/api/v1/rentals/", json=rental_data)
    assert response.status_code == 201
    data = response.json()
    assert data["inventory_id"] == 1
    assert data["customer_id"] == 1


@pytest.mark.asyncio
async def test_get_rentals(client: AsyncClient):
    """Happy-path: Get all rentals with pagination."""
    response = await client.get("/api/v1/rentals/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_rental_by_id(client: AsyncClient):
    """Happy-path: Get rental by ID."""
    # First create a rental
    rental_data = {"inventory_id": 1, "customer_id": 1, "staff_id": 1}
    create_response = await client.post("/api/v1/rentals/", json=rental_data)
    assert create_response.status_code == 201
    rental_id = create_response.json()["id"]

    # Then get it by ID
    response = await client.get(f"/api/v1/rentals/{rental_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rental_id


@pytest.mark.asyncio
async def test_update_rental(client: AsyncClient):
    """Happy-path: Update a rental."""
    # First create a rental
    rental_data = {"inventory_id": 1, "customer_id": 1, "staff_id": 1}
    create_response = await client.post("/api/v1/rentals/", json=rental_data)
    assert create_response.status_code == 201
    rental_id = create_response.json()["id"]

    # Then update it
    update_data = {"return_date": "2024-01-01T00:00:00"}
    response = await client.put(f"/api/v1/rentals/{rental_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rental_id


@pytest.mark.asyncio
async def test_delete_rental(client: AsyncClient):
    """Happy-path: Delete a rental."""
    # First create a rental
    rental_data = {"inventory_id": 1, "customer_id": 1, "staff_id": 1}
    create_response = await client.post("/api/v1/rentals/", json=rental_data)
    assert create_response.status_code == 201
    rental_id = create_response.json()["id"]

    # Then delete it
    response = await client.delete(f"/api/v1/rentals/{rental_id}")
    assert response.status_code == 204
