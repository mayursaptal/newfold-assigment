"""Rental Pydantic schemas for API request/response validation.

This module defines Pydantic schemas used for validating and serializing
rental data in API requests and responses. These schemas ensure type safety
and data validation at the API boundary.

Example:
    ```python
    from domain.schemas import RentalCreate, RentalRead
    
    # Create request
    rental_data = RentalCreate(
        inventory_id=1,
        customer_id=1,
        staff_id=1
    )
    
    # Read response
    rental = RentalRead(
        id=1,
        inventory_id=1,
        customer_id=1,
        staff_id=1,
        rental_date=datetime.now()
    )
    ```
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from pydantic import BaseModel


class RentalCreate(SQLModel):
    """Schema for creating a new rental.
    
    Used to validate incoming POST request data when creating a rental.
    Requires inventory, customer, and staff IDs.
    
    Attributes:
        inventory_id: ID of the inventory item being rented
        customer_id: ID of the customer renting the film
        staff_id: ID of the staff member processing the rental
        rental_date: Date and time of rental (defaults to current time if not provided)
    """
    inventory_id: int
    customer_id: int
    staff_id: int
    rental_date: Optional[datetime] = None  # Will default to now() if not provided


class RentalCreateRequest(BaseModel):
    """Schema for creating a rental via customer-specific endpoint.
    
    Used for POST /customers/{customer_id}/rentals endpoint where
    customer_id comes from the URL path, not the request body.
    
    Attributes:
        inventory_id: ID of the inventory item being rented
        staff_id: ID of the staff member processing the rental
        rental_date: Date and time of rental (defaults to current time if not provided)
    """
    inventory_id: int
    staff_id: int
    rental_date: Optional[datetime] = None  # Will default to now() if not provided


class RentalUpdate(SQLModel):
    """Schema for updating an existing rental.
    
    Used to validate incoming PUT/PATCH request data when updating a rental.
    Currently only supports updating the return_date.
    
    Attributes:
        return_date: Date and time when the film was returned
    """
    return_date: Optional[datetime] = None


class RentalRead(SQLModel):
    """Schema for reading rental data.
    
    Used to serialize rental data in API responses. Includes all rental
    information including timestamps.
    
    Attributes:
        id: Rental primary key
        inventory_id: ID of the rented inventory item
        customer_id: ID of the customer who rented
        staff_id: ID of the staff member who processed the rental
        rental_date: Date and time when rental was created
        return_date: Date and time when film was returned (None if not returned)
        last_update: Timestamp of last update
    """
    id: int
    inventory_id: int
    customer_id: int
    staff_id: int
    rental_date: datetime
    return_date: Optional[datetime] = None
    last_update: datetime

