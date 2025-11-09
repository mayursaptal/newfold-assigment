"""Film model."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum


class FilmRating(str, Enum):
    """Film rating enumeration."""
    G = "G"
    PG = "PG"
    PG13 = "PG-13"
    R = "R"
    NC17 = "NC-17"


class FilmBase(SQLModel):
    """Base film model."""
    title: str = Field(index=True)
    description: Optional[str] = None
    release_year: Optional[int] = None
    language_id: int  # Foreign key exists in DB, but not defined as FK in model to avoid SQLModel resolution issues
    rental_duration: int = Field(default=3)
    rental_rate: float = Field(default=4.99)
    length: Optional[int] = None
    replacement_cost: float = Field(default=19.99)
    rating: Optional[FilmRating] = None
    streaming_available: bool = Field(default=False)  # Boolean column with default FALSE


class Film(FilmBase, table=True):
    """Film entity."""
    __tablename__ = "film"
    
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"name": "film_id"})
    last_update: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )

