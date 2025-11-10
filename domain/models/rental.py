"""Rental domain model.

This module defines the Rental entity and related models using SQLModel.
The Rental model represents a film rental transaction in the database,
tracking when a customer rented a film and when it was returned.

Example:
    ```python
    from domain.models import Rental
    from datetime import datetime

    rental = Rental(
        inventory_id=1,
        customer_id=1,
        staff_id=1,
        rental_date=datetime.utcnow()
    )
    ```
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class RentalBase(SQLModel):
    """Base rental model with common attributes.

    This is the base class for Rental entities, containing all the common
    rental attributes that are shared between create, update, and read operations.

    Attributes:
        inventory_id: Foreign key to inventory table (not enforced in model to avoid SQLModel resolution issues)
        customer_id: Foreign key to customer table
        staff_id: Foreign key to staff table (not enforced in model to avoid SQLModel resolution issues)
        rental_date: Date and time when film was rented (defaults to current time)
        return_date: Date and time when film was returned (None if not yet returned)
    """

    inventory_id: int  # Foreign key exists in DB, but not defined as FK in model to avoid SQLModel resolution issues
    customer_id: int
    staff_id: int  # Foreign key exists in DB, but not defined as FK in model to avoid SQLModel resolution issues
    rental_date: datetime = Field(default_factory=datetime.utcnow)
    return_date: Optional[datetime] = None


class Rental(RentalBase, table=True):
    """Rental entity mapped to database table.

    This is the SQLModel entity that represents the 'rental' table in the
    database. It extends RentalBase with database-specific fields like
    primary key and timestamps.

    Attributes:
        id: Primary key (mapped to rental_id column in database)
        last_update: Timestamp of last update (auto-set by database)

    Note:
        The table name is explicitly set to 'rental' to match the Pagila
        database schema. The id field maps to 'rental_id' in the database.
    """

    __tablename__ = "rental"

    id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"name": "rental_id"}
    )
    last_update: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )
