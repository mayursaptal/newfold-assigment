"""Film API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from domain.models import FilmCreate, FilmUpdate, FilmRead
from domain.services import FilmService
from core.dependencies import get_film_service

router = APIRouter()


@router.post("/", response_model=FilmRead, status_code=status.HTTP_201_CREATED)
async def create_film(
    film: FilmCreate,
    service: FilmService = Depends(get_film_service),
):
    """
    Create a new film.
    
    Args:
        film: Film creation data
        service: Film service (injected)
        
    Returns:
        Created film
    """
    return await service.create_film(film)


@router.get("/", response_model=List[FilmRead])
async def get_films(
    skip: int = 0,
    limit: int = 100,
    service: FilmService = Depends(get_film_service),
):
    """
    Get all films with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: Film service (injected)
        
    Returns:
        List of films
    """
    return await service.get_films(skip=skip, limit=limit)


@router.get("/{film_id}", response_model=FilmRead)
async def get_film(
    film_id: int,
    service: FilmService = Depends(get_film_service),
):
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
):
    """
    Update a film.
    
    Args:
        film_id: Film ID
        film_update: Film update data
        service: Film service (injected)
        
    Returns:
        Updated film
        
    Raises:
        HTTPException: If film not found
    """
    film = await service.update_film(film_id, film_update)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film with id {film_id} not found",
        )
    return film


@router.delete("/{film_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_film(
    film_id: int,
    service: FilmService = Depends(get_film_service),
):
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

