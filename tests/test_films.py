"""Tests for film endpoints."""

import pytest
from httpx import AsyncClient
from domain.schemas import FilmCreate
from domain.models import FilmRating


@pytest.mark.asyncio
async def test_create_film(client: AsyncClient):
    """Test creating a film."""
    film_data = {
        "title": "Test Film",
        "description": "A test film",
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
    """Test getting all films."""
    response = await client.get("/api/v1/films/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_film_not_found(client: AsyncClient):
    """Test getting a non-existent film."""
    response = await client.get("/api/v1/films/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_film(client: AsyncClient):
    """Test updating a film."""
    # First create a film
    film_data = {
        "title": "Original Title",
        "language_id": 1,
    }
    create_response = await client.post("/api/v1/films/", json=film_data)
    assert create_response.status_code == 201
    film_id = create_response.json()["id"]
    
    # Update the film
    update_data = {"title": "Updated Title"}
    update_response = await client.put(f"/api/v1/films/{film_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_film(client: AsyncClient):
    """Test deleting a film."""
    # First create a film
    film_data = {
        "title": "Film to Delete",
        "language_id": 1,
    }
    create_response = await client.post("/api/v1/films/", json=film_data)
    assert create_response.status_code == 201
    film_id = create_response.json()["id"]
    
    # Delete the film
    delete_response = await client.delete(f"/api/v1/films/{film_id}")
    assert delete_response.status_code == 204
    
    # Verify it's deleted
    get_response = await client.get(f"/api/v1/films/{film_id}")
    assert get_response.status_code == 404

