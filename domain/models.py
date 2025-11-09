"""SQLModel entities for the domain."""

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
    language_id: int = Field(foreign_key="language.id")
    rental_duration: int = Field(default=3)
    rental_rate: float = Field(default=4.99)
    length: Optional[int] = None
    replacement_cost: float = Field(default=19.99)
    rating: Optional[FilmRating] = None


class Film(FilmBase, table=True):
    """Film entity."""
    __tablename__ = "film"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


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


class FilmRead(FilmBase):
    """Film read schema."""
    id: int
    created_at: datetime
    updated_at: datetime


class RentalBase(SQLModel):
    """Base rental model."""
    film_id: int = Field(foreign_key="film.id")
    customer_id: int
    rental_date: datetime = Field(default_factory=datetime.utcnow)
    return_date: Optional[datetime] = None


class Rental(RentalBase, table=True):
    """Rental entity."""
    __tablename__ = "rental"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RentalCreate(RentalBase):
    """Rental creation schema."""
    pass


class RentalUpdate(SQLModel):
    """Rental update schema."""
    return_date: Optional[datetime] = None


class RentalRead(RentalBase):
    """Rental read schema."""
    id: int
    created_at: datetime
    updated_at: datetime

