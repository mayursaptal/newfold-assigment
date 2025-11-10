"""Tests for film endpoints including validation tests.

This module contains happy-path tests and validation tests for film endpoints,
including tests for year constraint validation and other data validation.
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


# Validation Tests


@pytest.mark.asyncio
async def test_create_film_invalid_year_too_low(client: AsyncClient) -> None:
    """Test validation: Create film with year below 1901 should fail."""
    film_data = {
        "title": "Ancient Film",
        "language_id": 1,
        "rental_duration": 3,
        "rental_rate": 4.99,
        "replacement_cost": 19.99,
        "release_year": 1900,  # Below minimum (1901)
    }
    response = await client.post("/api/v1/films/", json=film_data)
    assert response.status_code == 422  # Pydantic validation error
    data = response.json()
    assert "release year must be between 1901 and 2155" in data["detail"][0]["msg"].lower()


@pytest.mark.asyncio
async def test_create_film_invalid_year_too_high(client: AsyncClient) -> None:
    """Test validation: Create film with year above 2155 should fail."""
    film_data = {
        "title": "Future Film",
        "language_id": 1,
        "rental_duration": 3,
        "rental_rate": 4.99,
        "replacement_cost": 19.99,
        "release_year": 2156,  # Above maximum (2155)
    }
    response = await client.post("/api/v1/films/", json=film_data)
    assert response.status_code == 422  # Pydantic validation error
    data = response.json()
    assert "release year must be between 1901 and 2155" in data["detail"][0]["msg"].lower()


@pytest.mark.asyncio
async def test_create_film_valid_year_boundaries(client: AsyncClient) -> None:
    """Test validation: Create film with valid boundary years should succeed."""
    # Test minimum valid year (1901)
    film_data_min = {
        "title": "Early Film",
        "language_id": 1,
        "rental_duration": 3,
        "rental_rate": 4.99,
        "replacement_cost": 19.99,
        "release_year": 1901,
    }
    response = await client.post("/api/v1/films/", json=film_data_min)
    assert response.status_code == 201
    data = response.json()
    assert data["release_year"] == 1901

    # Test maximum valid year (2155)
    film_data_max = {
        "title": "Future Film",
        "language_id": 1,
        "rental_duration": 3,
        "rental_rate": 4.99,
        "replacement_cost": 19.99,
        "release_year": 2155,
    }
    response = await client.post("/api/v1/films/", json=film_data_max)
    assert response.status_code == 201
    data = response.json()
    assert data["release_year"] == 2155


@pytest.mark.asyncio
async def test_create_film_negative_rental_duration(client: AsyncClient) -> None:
    """Test validation: Create film with negative rental duration should fail."""
    film_data = {
        "title": "Invalid Duration Film",
        "language_id": 1,
        "rental_duration": -1,  # Invalid negative duration
        "rental_rate": 4.99,
        "replacement_cost": 19.99,
    }
    response = await client.post("/api/v1/films/", json=film_data)
    assert response.status_code == 422  # Pydantic validation error
    data = response.json()
    assert "rental duration must be positive" in data["detail"][0]["msg"].lower()


@pytest.mark.asyncio
async def test_create_film_negative_rental_rate(client: AsyncClient) -> None:
    """Test validation: Create film with negative rental rate should fail."""
    film_data = {
        "title": "Invalid Rate Film",
        "language_id": 1,
        "rental_duration": 3,
        "rental_rate": -4.99,  # Invalid negative rate
        "replacement_cost": 19.99,
    }
    response = await client.post("/api/v1/films/", json=film_data)
    assert response.status_code == 422  # Pydantic validation error
    data = response.json()
    assert "amount must be positive" in data["detail"][0]["msg"].lower()


@pytest.mark.asyncio
async def test_create_film_negative_length(client: AsyncClient) -> None:
    """Test validation: Create film with negative length should fail."""
    film_data = {
        "title": "Invalid Length Film",
        "language_id": 1,
        "rental_duration": 3,
        "rental_rate": 4.99,
        "replacement_cost": 19.99,
        "length": -120,  # Invalid negative length
    }
    response = await client.post("/api/v1/films/", json=film_data)
    assert response.status_code == 422  # Pydantic validation error
    data = response.json()
    assert "film length must be positive" in data["detail"][0]["msg"].lower()


@pytest.mark.asyncio
async def test_update_film_invalid_year(client: AsyncClient) -> None:
    """Test validation: Update film with invalid year should fail."""
    # First create a valid film
    film_data = {
        "title": "Film to Update",
        "language_id": 1,
        "rental_duration": 3,
        "rental_rate": 4.99,
        "replacement_cost": 19.99,
        "release_year": 2000,
    }
    create_response = await client.post("/api/v1/films/", json=film_data)
    assert create_response.status_code == 201
    film_id = create_response.json()["id"]

    # Try to update with invalid year
    update_data = {"release_year": 1800}  # Below minimum (1901)
    response = await client.put(f"/api/v1/films/{film_id}", json=update_data)
    assert response.status_code == 422  # Pydantic validation error
    data = response.json()
    assert "release year must be between 1901 and 2155" in data["detail"][0]["msg"].lower()


@pytest.mark.asyncio
async def test_update_film_valid_year(client: AsyncClient) -> None:
    """Test validation: Update film with valid year should succeed."""
    # First create a valid film
    film_data = {
        "title": "Film to Update Valid",
        "language_id": 1,
        "rental_duration": 3,
        "rental_rate": 4.99,
        "replacement_cost": 19.99,
        "release_year": 2000,
    }
    create_response = await client.post("/api/v1/films/", json=film_data)
    assert create_response.status_code == 201
    film_id = create_response.json()["id"]

    # Update with valid year
    update_data = {"release_year": 2020}  # Valid year
    response = await client.put(f"/api/v1/films/{film_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["release_year"] == 2020
