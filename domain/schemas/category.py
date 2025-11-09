"""Category Pydantic schemas for API request/response validation.

This module defines Pydantic schemas used for validating and serializing
category data in API requests and responses. Categories are read-only
in this application (no create/update endpoints).

Example:
    ```python
    from domain.schemas import CategoryRead
    
    # Read response
    category = CategoryRead(
        id=1,
        name="Action",
        last_update=datetime.now()
    )
    ```
"""

from datetime import datetime
from sqlmodel import SQLModel
from domain.models.category import CategoryBase


class CategoryRead(CategoryBase):
    """Schema for reading category data.
    
    Used to serialize category data in API responses. Includes the
    category ID and last_update timestamp in addition to category name.
    
    Attributes:
        id: Category primary key
        name: Category name (inherited from CategoryBase)
        last_update: Timestamp of last update
    """
    id: int
    last_update: datetime

