"""Rental model."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class RentalBase(SQLModel):
    """Base rental model."""
    inventory_id: int  # Foreign key exists in DB, but not defined as FK in model to avoid SQLModel resolution issues
    customer_id: int
    staff_id: int  # Foreign key exists in DB, but not defined as FK in model to avoid SQLModel resolution issues
    rental_date: datetime = Field(default_factory=datetime.utcnow)
    return_date: Optional[datetime] = None


class Rental(RentalBase, table=True):
    """Rental entity."""
    __tablename__ = "rental"
    
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"name": "rental_id"})
    last_update: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )

