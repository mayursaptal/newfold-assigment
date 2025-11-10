"""Film API routes.

This module defines FastAPI routes for film-related endpoints. It provides
RESTful API endpoints for creating, reading, updating, and deleting films,
with support for pagination and category filtering.

Endpoints:
    POST /api/v1/films/ - Create a new film
    GET /api/v1/films/ - Get all films with pagination and optional category filter
    GET /api/v1/films/{film_id} - Get film by ID
    PUT /api/v1/films/{film_id} - Update a film
    DELETE /api/v1/films/{film_id} - Delete a film

Example:
    ```python
    # Create a film
    POST /api/v1/films/
    {
        "title": "The Matrix",
        "language_id": 1,
        "rental_duration": 3
    }

    # Get films by category
    GET /api/v1/films/?category=Action&skip=0&limit=10
    ```
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from domain.schemas import FilmCreate, FilmUpdate, FilmRead
from domain.services import FilmService
from core.dependencies import get_film_service

router = APIRouter()


@router.post("/", response_model=FilmRead, status_code=status.HTTP_201_CREATED)
async def create_film(
    film: FilmCreate,
    service: FilmService = Depends(get_film_service),
) -> FilmRead:
    """
    Create a new film.

    Args:
        film: Film creation data
        service: Film service (injected)

    Returns:
        Created film

    Raises:
        HTTPException: 400 if validation fails or database constraint is violated
        HTTPException: 500 if an unexpected error occurs
    """
    try:
        return await service.create_film(film)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation error: {str(e)}"
        )
    except IntegrityError as e:
        # Handle database constraint violations
        error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
        if "year_check" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Release year must be between 1901 and 2155 (inclusive)",
            )
        elif "check constraint" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data validation failed: one or more values violate database constraints",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity error: the provided data violates database constraints",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the film",
        )


@router.get("/", response_model=List[FilmRead])
async def get_films(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    service: FilmService = Depends(get_film_service),
) -> List[FilmRead]:
    """
    Get all films with pagination and optional category filter.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        category: Optional category name to filter by (?category=Action)
        service: Film service (injected)

    Returns:
        List of films
    """
    return await service.get_films(skip=skip, limit=limit, category=category)


@router.get("/{film_id}", response_model=FilmRead)
async def get_film(
    film_id: int,
    service: FilmService = Depends(get_film_service),
) -> FilmRead:
    """
    Get film by ID.

    Args:
        film_id: Film ID
        service: Film service (injected)

    Returns:
        Film

    Raises:
        HTTPException: If film not found
    """
    film = await service.get_film(film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film with id {film_id} not found",
        )
    return film


@router.put("/{film_id}", response_model=FilmRead)
async def update_film(
    film_id: int,
    film_update: FilmUpdate,
    service: FilmService = Depends(get_film_service),
) -> FilmRead:
    """
    Update a film.

    Args:
        film_id: Film ID
        film_update: Film update data
        service: Film service (injected)

    Returns:
        Updated film

    Raises:
        HTTPException: 400 if validation fails or database constraint is violated
        HTTPException: 404 if film not found
        HTTPException: 500 if an unexpected error occurs
    """
    try:
        film = await service.update_film(film_id, film_update)
        if not film:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Film with id {film_id} not found",
            )
        return film
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation error: {str(e)}"
        )
    except IntegrityError as e:
        # Handle database constraint violations
        error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
        if "year_check" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Release year must be between 1901 and 2155 (inclusive)",
            )
        elif "check constraint" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data validation failed: one or more values violate database constraints",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity error: the provided data violates database constraints",
            )
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without modification
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the film",
        )


@router.delete("/{film_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_film(
    film_id: int,
    service: FilmService = Depends(get_film_service),
) -> None:
    """
    Delete a film.

    Args:
        film_id: Film ID
        service: Film service (injected)

    Raises:
        HTTPException: If film not found
    """
    deleted = await service.delete_film(film_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film with id {film_id} not found",
        )
    # No return for 204 status code
