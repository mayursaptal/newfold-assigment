"""Rental API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from domain.schemas import RentalCreate, RentalUpdate, RentalRead
from domain.services import RentalService
from core.dependencies import get_rental_service

router = APIRouter()


@router.post("/", response_model=RentalRead, status_code=status.HTTP_201_CREATED)
async def create_rental(
    rental: RentalCreate,
    service: RentalService = Depends(get_rental_service),
):
    """
    Create a new rental.
    
    Args:
        rental: Rental creation data
        service: Rental service (injected)
        
    Returns:
        Created rental
    """
    return await service.create_rental(rental)


@router.get("/", response_model=List[RentalRead])
async def get_rentals(
    skip: int = 0,
    limit: int = 100,
    service: RentalService = Depends(get_rental_service),
):
    """
    Get all rentals with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: Rental service (injected)
        
    Returns:
        List of rentals
    """
    return await service.get_rentals(skip=skip, limit=limit)


@router.get("/{rental_id}", response_model=RentalRead)
async def get_rental(
    rental_id: int,
    service: RentalService = Depends(get_rental_service),
):
    """
    Get rental by ID.
    
    Args:
        rental_id: Rental ID
        service: Rental service (injected)
        
    Returns:
        Rental
        
    Raises:
        HTTPException: If rental not found
    """
    rental = await service.get_rental(rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with id {rental_id} not found",
        )
    return rental


@router.put("/{rental_id}", response_model=RentalRead)
async def update_rental(
    rental_id: int,
    rental_update: RentalUpdate,
    service: RentalService = Depends(get_rental_service),
):
    """
    Update a rental.
    
    Args:
        rental_id: Rental ID
        rental_update: Rental update data
        service: Rental service (injected)
        
    Returns:
        Updated rental
        
    Raises:
        HTTPException: If rental not found
    """
    rental = await service.update_rental(rental_id, rental_update)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with id {rental_id} not found",
        )
    return rental


@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rental(
    rental_id: int,
    service: RentalService = Depends(get_rental_service),
):
    """
    Delete a rental.
    
    Args:
        rental_id: Rental ID
        service: Rental service (injected)
        
    Raises:
        HTTPException: If rental not found
    """
    deleted = await service.delete_rental(rental_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with id {rental_id} not found",
        )

