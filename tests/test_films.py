"""Tests for film endpoints - one happy-path test per endpoint.

This module contains pytest tests for all film-related API endpoints.
Each endpoint has exactly one happy-path test that verifies successful
operation with valid input data.

Test Coverage:
    - POST /api/v1/films/ - Create film
    - GET /api/v1/films/ - Get all films with pagination
    - GET /api/v1/films/{film_id} - Get film by ID
    - PUT /api/v1/films/{film_id} - Update film
    - DELETE /api/v1/films/{film_id} - Delete film
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_film(client: AsyncClient):
    """Happy-path: Create a film."""
    film_data = {
        "title": "Test Film",
        "description": "A test film description",
        "release_year": 2024,
        "language_id": 1,
        "rental_duration": 3,
        "rental_rate": 4.99,
        "length": 120,
        "replacement_cost": 19.99,
        "rating": "PG-13",
    }
    
    response = await client.post("/api/v1/films/", json=film_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == film_data["title"]
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_get_films(client: AsyncClient):
    """Happy-path: Get all films with pagination."""
    response = await client.get("/api/v1/films/?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_film_by_id(client: AsyncClient):
    """Happy-path: Get film by ID."""
    # First create a film
    film_data = {
        "title": "Film to Get",
        "language_id": 1,
    }
    create_response = await client.post("/api/v1/films/", json=film_data)
    film_id = create_response.json()["id"]
    
    # Get the film
    response = await client.get(f"/api/v1/films/{film_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == film_id
    assert data["title"] == film_data["title"]


@pytest.mark.asyncio
async def test_update_film(client: AsyncClient):
    """Happy-path: Update a film."""
    # First create a film
    film_data = {
        "title": "Original Title",
        "language_id": 1,
    }
    create_response = await client.post("/api/v1/films/", json=film_data)
    film_id = create_response.json()["id"]
    
    # Update the film
    update_data = {"title": "Updated Title"}
    response = await client.put(f"/api/v1/films/{film_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_film(client: AsyncClient):
    """Happy-path: Delete a film."""
    # First create a film
    film_data = {
        "title": "Film to Delete",
        "language_id": 1,
    }
    create_response = await client.post("/api/v1/films/", json=film_data)
    film_id = create_response.json()["id"]
    
    # Delete the film
    response = await client.delete(f"/api/v1/films/{film_id}")
    assert response.status_code == 204
