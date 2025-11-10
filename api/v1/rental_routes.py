"""Rental API routes.

This module defines FastAPI routes for rental-related endpoints. It provides
RESTful API endpoints for creating, reading, updating, and deleting rentals.

Endpoints:
    POST /api/v1/rentals/ - Create a new rental
    GET /api/v1/rentals/ - Get all rentals with pagination
    GET /api/v1/rentals/{rental_id} - Get rental by ID
    PUT /api/v1/rentals/{rental_id} - Update a rental
    DELETE /api/v1/rentals/{rental_id} - Delete a rental

Example:
    ```python
    # Create a rental
    POST /api/v1/rentals/
    {
        "inventory_id": 1,
        "customer_id": 1,
        "staff_id": 1
    }
    ```
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from domain.schemas import RentalCreate, RentalUpdate, RentalRead
from domain.services import RentalService
from core.dependencies import get_rental_service

router = APIRouter()


@router.post("/", response_model=RentalRead, status_code=status.HTTP_201_CREATED)
async def create_rental(
    rental: RentalCreate,
    service: RentalService = Depends(get_rental_service),
) -> RentalRead:
    """
    Create a new rental.

    Args:
        rental: Rental creation data
        service: Rental service (injected)

    Returns:
        Created rental

    Raises:
        HTTPException: 400 if validation fails or database constraint is violated
        HTTPException: 500 if an unexpected error occurs
    """
    try:
        return await service.create_rental(rental)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation error: {str(e)}"
        )
    except IntegrityError as e:
        # Handle database constraint violations
        error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
        if (
            "idx_unq_rental_rental_date_inventory_id_customer_id" in error_msg
            or "duplicate key value" in error_msg
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This rental already exists. The same customer cannot rent the same item at the same time.",
            )
        elif "foreign key constraint" in error_msg.lower():
            if "inventory_id" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid inventory_id: the specified inventory item does not exist",
                )
            elif "customer_id" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid customer_id: the specified customer does not exist",
                )
            elif "staff_id" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid staff_id: the specified staff member does not exist",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reference: one or more referenced entities do not exist",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity error: the provided data violates database constraints",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the rental",
        )


@router.get("/", response_model=List[RentalRead])
async def get_rentals(
    skip: int = 0,
    limit: int = 100,
    service: RentalService = Depends(get_rental_service),
) -> List[RentalRead]:
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
) -> RentalRead:
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
) -> RentalRead:
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
) -> None:
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
    # No return for 204 status code
