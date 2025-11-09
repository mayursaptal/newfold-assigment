"""Category schemas."""

from datetime import datetime
from sqlmodel import SQLModel
from domain.models.category import CategoryBase


class CategoryRead(CategoryBase):
    """Category read schema."""
    id: int
    last_update: datetime

