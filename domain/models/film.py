"""Film domain model.

This module defines the Film entity and related models using SQLModel.
The Film model represents a movie in the database with all its attributes
including title, description, rating, and rental information.

Example:
    ```python
    from domain.models import Film
    
    film = Film(
        title="The Matrix",
        language_id=1,
        rental_duration=3,
        rental_rate=4.99
    )
    ```
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum


class FilmRating(str, Enum):
    """Film rating enumeration.
    
    Represents the Motion Picture Association of America (MPAA) film
    rating system used to classify films based on content.
    
    Attributes:
        G: General audiences - all ages admitted
        PG: Parental guidance suggested
        PG13: Parents strongly cautioned - some material may be inappropriate for children under 13
        R: Restricted - children under 17 require accompanying parent or adult guardian
        NC17: No one 17 and under admitted
    """
    G = "G"
    PG = "PG"
    PG13 = "PG-13"
    R = "R"
    NC17 = "NC-17"


class FilmBase(SQLModel):
    """Base film model with common attributes.
    
    This is the base class for Film entities, containing all the common
    film attributes that are shared between create, update, and read operations.
    
    Attributes:
        title: Film title (indexed for faster searches)
        description: Film description/synopsis
        release_year: Year the film was released
        language_id: Foreign key to language table (not enforced in model to avoid SQLModel resolution issues)
        rental_duration: Number of days film can be rented (default: 3)
        rental_rate: Cost per rental period (default: 4.99)
        length: Film length in minutes
        replacement_cost: Cost to replace if lost/damaged (default: 19.99)
        rating: MPAA rating (G, PG, PG-13, R, NC-17)
        streaming_available: Whether film is available for streaming (default: False)
    """
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
    """Film entity mapped to database table.
    
    This is the SQLModel entity that represents the 'film' table in the
    database. It extends FilmBase with database-specific fields like
    primary key and timestamps.
    
    Attributes:
        id: Primary key (mapped to film_id column in database)
        last_update: Timestamp of last update (auto-set by database)
        
    Note:
        The table name is explicitly set to 'film' to match the Pagila
        database schema. The id field maps to 'film_id' in the database.
    """
    __tablename__ = "film"
    
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"name": "film_id"})
    last_update: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )

