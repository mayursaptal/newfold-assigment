"""Film Pydantic schemas for API request/response validation.

This module defines Pydantic schemas used for validating and serializing
film data in API requests and responses. These schemas ensure type safety
and data validation at the API boundary.

Example:
    ```python
    from domain.schemas import FilmCreate, FilmRead
    
    # Create request
    film_data = FilmCreate(title="The Matrix", language_id=1)
    
    # Read response
    film = FilmRead(id=1, title="The Matrix", last_update=datetime.now())
    ```
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from pydantic import BaseModel
from domain.models.film import FilmBase, FilmRating


class FilmCreate(FilmBase):
    """Schema for creating a new film.
    
    Used to validate incoming POST request data when creating a film.
    Inherits all fields from FilmBase, requiring all mandatory fields.
    
    Attributes:
        Inherits all attributes from FilmBase.
    """
    pass


class FilmUpdate(SQLModel):
    """Schema for updating an existing film.
    
    Used to validate incoming PUT/PATCH request data when updating a film.
    All fields are optional, allowing partial updates.
    
    Attributes:
        title: Updated film title
        description: Updated film description
        release_year: Updated release year
        rental_duration: Updated rental duration in days
        rental_rate: Updated rental rate
        length: Updated film length in minutes
        replacement_cost: Updated replacement cost
        rating: Updated MPAA rating
        streaming_available: Updated streaming availability flag
    """
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
    """Schema for reading film data.
    
    Used to serialize film data in API responses. Includes the film ID
    and last_update timestamp in addition to all FilmBase fields.
    
    Attributes:
        id: Film primary key
        last_update: Timestamp of last update
        Inherits all attributes from FilmBase.
    """
    id: int
    last_update: datetime


class FilmSummaryRequest(BaseModel):
    """Request schema for AI-generated film summary.
    
    Used to validate requests to the AI film summary endpoint.
    
    Attributes:
        film_id: ID of the film to generate a summary for
    """
    film_id: int


class FilmSummaryResponse(BaseModel):
    """Response schema for AI-generated film summary.
    
    Used to serialize AI-generated film summaries in API responses.
    
    Attributes:
        title: Film title
        rating: Film rating (as string)
        recommended: Boolean indicating if film is recommended
    """
    title: str
    rating: str
    recommended: bool

