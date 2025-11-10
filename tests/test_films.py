"""Happy-path tests for film endpoints.

This module contains one happy-path test per film endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_film(client: AsyncClient) -> None:
    """Happy-path: Create a new film."""
    film_data = {
        "title": "Test Film",
        "language_id": 1,
        "rental_duration": 3,
        "rental_rate": 4.99,
        "replacement_cost": 19.99,
    }
    response = await client.post("/api/v1/films/", json=film_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Film"
    assert data["rental_duration"] == 3


@pytest.mark.asyncio
async def test_get_films(client: AsyncClient) -> None:
    """Happy-path: Get all films with pagination."""
    response = await client.get("/api/v1/films/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_film_by_id(client: AsyncClient) -> None:
    """Happy-path: Get film by ID."""
    # First create a film
    film_data = {"title": "Test Film ID", "language_id": 1, "rental_duration": 3}
    create_response = await client.post("/api/v1/films/", json=film_data)
    assert create_response.status_code == 201
    film_id = create_response.json()["id"]

    # Then get it by ID
    response = await client.get(f"/api/v1/films/{film_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == film_id
    assert data["title"] == "Test Film ID"


@pytest.mark.asyncio
async def test_update_film(client: AsyncClient) -> None:
    """Happy-path: Update a film."""
    # First create a film
    film_data = {"title": "Original Title", "language_id": 1, "rental_duration": 3}
    create_response = await client.post("/api/v1/films/", json=film_data)
    assert create_response.status_code == 201
    film_id = create_response.json()["id"]

    # Then update it
    update_data = {"title": "Updated Title"}
    response = await client.put(f"/api/v1/films/{film_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_film(client: AsyncClient) -> None:
    """Happy-path: Delete a film."""
    # First create a film
    film_data = {"title": "Film to Delete", "language_id": 1, "rental_duration": 3}
    create_response = await client.post("/api/v1/films/", json=film_data)
    assert create_response.status_code == 201
    film_id = create_response.json()["id"]

    # Then delete it
    response = await client.delete(f"/api/v1/films/{film_id}")
    assert response.status_code == 204
