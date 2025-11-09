"""Tests for rental endpoints - one happy-path test per endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_rental(client: AsyncClient):
    """Happy-path: Create a rental."""
    rental_data = {
        "inventory_id": 1,
        "customer_id": 1,
        "staff_id": 1,
    }
    
    response = await client.post("/api/v1/rentals/", json=rental_data)
    assert response.status_code == 201
    data = response.json()
    assert data["inventory_id"] == rental_data["inventory_id"]
    assert data["customer_id"] == rental_data["customer_id"]
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_get_rentals(client: AsyncClient):
    """Happy-path: Get all rentals with pagination."""
    response = await client.get("/api/v1/rentals/?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_rental_by_id(client: AsyncClient):
    """Happy-path: Get rental by ID."""
    # First create a rental
    rental_data = {
        "inventory_id": 1,
        "customer_id": 1,
        "staff_id": 1,
    }
    create_response = await client.post("/api/v1/rentals/", json=rental_data)
    rental_id = create_response.json()["id"]
    
    # Get the rental
    response = await client.get(f"/api/v1/rentals/{rental_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rental_id


@pytest.mark.asyncio
async def test_update_rental(client: AsyncClient):
    """Happy-path: Update a rental."""
    # First create a rental
    rental_data = {
        "inventory_id": 1,
        "customer_id": 1,
        "staff_id": 1,
    }
    create_response = await client.post("/api/v1/rentals/", json=rental_data)
    rental_id = create_response.json()["id"]
    
    # Update the rental
    from datetime import datetime
    update_data = {"return_date": datetime.utcnow().isoformat()}
    response = await client.put(f"/api/v1/rentals/{rental_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["return_date"] is not None


@pytest.mark.asyncio
async def test_delete_rental(client: AsyncClient):
    """Happy-path: Delete a rental."""
    # First create a rental
    rental_data = {
        "inventory_id": 1,
        "customer_id": 1,
        "staff_id": 1,
    }
    create_response = await client.post("/api/v1/rentals/", json=rental_data)
    rental_id = create_response.json()["id"]
    
    # Delete the rental
    response = await client.delete(f"/api/v1/rentals/{rental_id}")
    assert response.status_code == 204
