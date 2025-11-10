"""Customer API routes.

This module defines FastAPI routes for customer-related endpoints. It provides
endpoints for managing customer rentals with authentication requirements.

Endpoints:
    GET /api/v1/customers/{customer_id}/rentals - Get all rentals for a customer
    POST /api/v1/customers/{customer_id}/rentals - Create a rental for a customer (requires Bearer token with 'dvd_' prefix)

Example:
    ```python
    # Get customer rentals
    GET /api/v1/customers/1/rentals?skip=0&limit=10

    # Create rental (requires Bearer token)
    POST /api/v1/customers/1/rentals
    Authorization: Bearer dvd_test_token_123
    {
        "inventory_id": 1,
        "staff_id": 1
    }
    ```
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from domain.services import RentalService
from domain.schemas import RentalRead, RentalCreate, RentalCreateRequest
from core.dependencies import get_rental_service, get_dvd_token_guard

router = APIRouter()


@router.get("/{customer_id}/rentals", response_model=List[RentalRead])
async def get_customer_rentals(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    service: RentalService = Depends(get_rental_service),
) -> List[RentalRead]:
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


@router.post(
    "/{customer_id}/rentals", response_model=RentalRead, status_code=status.HTTP_201_CREATED
)
async def create_customer_rental(
    customer_id: int,
    rental_data: RentalCreateRequest,
    service: RentalService = Depends(get_rental_service),
    token: dict = Depends(get_dvd_token_guard()),  # Bearer token required with 'dvd_' prefix
) -> RentalRead:
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
