"""Film schemas."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from domain.models.film import FilmBase, FilmRating


class FilmCreate(FilmBase):
    """Film creation schema."""
    pass


class FilmUpdate(SQLModel):
    """Film update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None
    rental_duration: Optional[int] = None
    rental_rate: Optional[float] = None
    length: Optional[int] = None
    replacement_cost: Optional[float] = None
    rating: Optional[FilmRating] = None
    streaming_available: Optional[bool] = None


class FilmRead(FilmBase):
    """Film read schema."""
    id: int
    last_update: datetime

