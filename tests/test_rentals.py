"""Tests for rental endpoints."""

import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
async def test_create_rental(client: AsyncClient):
    """Test creating a rental."""
    # First create a film
    film_data = {
        "title": "Rental Film",
        "language_id": 1,
    }
    film_response = await client.post("/api/v1/films/", json=film_data)
    film_id = film_response.json()["id"]
    
    # Create a rental
    rental_data = {
        "film_id": film_id,
        "customer_id": 1,
        "rental_date": datetime.utcnow().isoformat(),
    }
    
    response = await client.post("/api/v1/rentals/", json=rental_data)
    assert response.status_code == 201
    data = response.json()
    assert data["film_id"] == film_id
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_get_rentals(client: AsyncClient):
    """Test getting all rentals."""
    response = await client.get("/api/v1/rentals/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_rental_not_found(client: AsyncClient):
    """Test getting a non-existent rental."""
    response = await client.get("/api/v1/rentals/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_rental(client: AsyncClient):
    """Test updating a rental."""
    # First create a film and rental
    film_data = {"title": "Test Film", "language_id": 1}
    film_response = await client.post("/api/v1/films/", json=film_data)
    film_id = film_response.json()["id"]
    
    rental_data = {
        "film_id": film_id,
        "customer_id": 1,
    }
    create_response = await client.post("/api/v1/rentals/", json=rental_data)
    rental_id = create_response.json()["id"]
    
    # Update the rental
    update_data = {"return_date": datetime.utcnow().isoformat()}
    update_response = await client.put(
        f"/api/v1/rentals/{rental_id}",
        json=update_data
    )
    assert update_response.status_code == 200
    assert update_response.json()["return_date"] is not None

