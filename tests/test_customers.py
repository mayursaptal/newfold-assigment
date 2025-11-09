"""Happy-path tests for customer endpoints.

This module contains one happy-path test per customer endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_customer_rentals(client: AsyncClient):
    """Happy-path: Get all rentals for a customer."""
    # Use customer ID 1 (assuming it exists in test DB)
    response = await client.get("/api/v1/customers/1/rentals?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_customer_rental(client: AsyncClient):
    """Happy-path: Create a rental for a customer with Bearer token."""
    rental_data = {
        "inventory_id": 1,
        "staff_id": 1
    }
    headers = {"Authorization": "Bearer dvd_test_token"}
    response = await client.post(
        "/api/v1/customers/1/rentals",
        json=rental_data,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["customer_id"] == 1
    assert data["inventory_id"] == 1

