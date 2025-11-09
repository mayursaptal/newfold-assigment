"""Tests for customer endpoints - one happy-path test per endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_customer_rentals(client: AsyncClient):
    """Happy-path: Get all rentals for a specific customer."""
    customer_id = 1
    response = await client.get(f"/api/v1/customers/{customer_id}/rentals?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_customer_rental(client: AsyncClient):
    """Happy-path: Create a rental for a customer with Bearer token."""
    customer_id = 1
    rental_data = {
        "inventory_id": 1,
        "staff_id": 1,
    }
    
    # Use Bearer token with 'dvd_' prefix as required
    headers = {"Authorization": "Bearer dvd_test_token_123"}
    
    response = await client.post(
        f"/api/v1/customers/{customer_id}/rentals",
        json=rental_data,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["inventory_id"] == rental_data["inventory_id"]
    assert data["id"] is not None

