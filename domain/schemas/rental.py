"""Rental schemas."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel


class RentalCreate(SQLModel):
    """Rental creation schema."""
    inventory_id: int
    customer_id: int
    staff_id: int
    rental_date: Optional[datetime] = None  # Will default to now() if not provided


class RentalUpdate(SQLModel):
    """Rental update schema."""
    return_date: Optional[datetime] = None


class RentalRead(SQLModel):
    """Rental read schema."""
    id: int
    inventory_id: int
    customer_id: int
    staff_id: int
    rental_date: datetime
    return_date: Optional[datetime] = None
    last_update: datetime

