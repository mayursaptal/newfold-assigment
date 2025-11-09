"""Customer API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from domain.services import RentalService
from domain.models import RentalRead
from core.dependencies import get_rental_service
from core.auth import verify_dvd_token

router = APIRouter()


class RentalCreateRequest(BaseModel):
    """Rental creation request model."""
    inventory_id: int
    staff_id: int
    rental_date: Optional[datetime] = None  # Will default to now() if not provided


@router.get("/{customer_id}/rentals", response_model=List[RentalRead])
async def get_customer_rentals(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    service: RentalService = Depends(get_rental_service),
):
    """
    Get all rentals for a specific customer with pagination.
    
    Args:
        customer_id: Customer ID
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        service: Rental service (injected)
        
    Returns:
        List of customer rentals
    """
    rentals = await service.get_rentals(skip=skip, limit=limit, customer_id=customer_id)
    return rentals


@router.post("/{customer_id}/rentals", response_model=RentalRead, status_code=status.HTTP_201_CREATED)
async def create_customer_rental(
    customer_id: int,
    rental_data: RentalCreateRequest,
    service: RentalService = Depends(get_rental_service),
    token: dict = Depends(verify_dvd_token),  # Bearer token required with 'dvd_' prefix
):
    """
    Create a new rental for a customer.
    
    Args:
        customer_id: Customer ID
        rental_data: Rental creation data (inventory_id, staff_id, rental_date)
        service: Rental service (injected)
        token: Verified Bearer token (must start with 'dvd_')
        
    Returns:
        Created rental
        
    Raises:
        HTTPException: If customer not found or validation fails
    """
    from domain.models import RentalCreate
    
    # Create rental with customer_id from path
    rental_create = RentalCreate(
        inventory_id=rental_data.inventory_id,
        customer_id=customer_id,
        staff_id=rental_data.staff_id,
        rental_date=rental_data.rental_date,  # Will default to now() in repository
    )
    
    try:
        rental = await service.create_rental(rental_create)
        return rental
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create rental: {str(e)}",
        )

