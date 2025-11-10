"""Category domain model.

This module defines the Category entity and related models using SQLModel.
The Category model represents a film category/genre in the database,
used to classify films (e.g., Action, Comedy, Drama).

Example:
    ```python
    from domain.models import Category

    category = Category(name="Action")
    ```
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class CategoryBase(SQLModel):
    """Base category model with common attributes.

    This is the base class for Category entities, containing all the common
    category attributes that are shared between create, update, and read operations.

    Attributes:
        name: Category name (indexed for faster searches)
    """

    name: str = Field(index=True)


class Category(CategoryBase, table=True):
    """Category entity mapped to database table.

    This is the SQLModel entity that represents the 'category' table in the
    database. It extends CategoryBase with database-specific fields like
    primary key and timestamps.

    Attributes:
        id: Primary key (mapped to category_id column in database)
        last_update: Timestamp of last update (auto-set by database)

    Note:
        The table name is explicitly set to 'category' to match the Pagila
        database schema. The id field maps to 'category_id' in the database.
    """

    __tablename__ = "category"

    id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"name": "category_id"}
    )
    last_update: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )
