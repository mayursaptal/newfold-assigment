"""Category model."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class CategoryBase(SQLModel):
    """Base category model."""
    name: str = Field(index=True)


class Category(CategoryBase, table=True):
    """Category entity."""
    __tablename__ = "category"
    
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"name": "category_id"})
    last_update: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )

