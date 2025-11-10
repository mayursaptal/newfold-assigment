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
from pydantic import BaseModel, field_validator
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
        release_year: Updated release year (must be between 1901 and 2155)
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

    @field_validator("release_year")
    @classmethod
    def validate_release_year(cls, v: Optional[int]) -> Optional[int]:
        """Validate release year matches database constraint.

        The database has a year domain constraint that only allows years
        between 1901 and 2155 (inclusive). This validator ensures the
        application validates this constraint before attempting database operations.

        Args:
            v: The release year value to validate

        Returns:
            The validated release year

        Raises:
            ValueError: If the year is outside the valid range (1901-2155)
        """
        if v is not None:
            if v < 1901 or v > 2155:
                raise ValueError(
                    f"Release year must be between 1901 and 2155 (inclusive). Got: {v}"
                )
        return v

    @field_validator("rental_duration")
    @classmethod
    def validate_rental_duration(cls, v: Optional[int]) -> Optional[int]:
        """Validate rental duration is positive.

        Args:
            v: The rental duration value to validate

        Returns:
            The validated rental duration

        Raises:
            ValueError: If the rental duration is not positive
        """
        if v is not None and v <= 0:
            raise ValueError(f"Rental duration must be positive. Got: {v}")
        return v

    @field_validator("rental_rate", "replacement_cost")
    @classmethod
    def validate_positive_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate monetary amounts are positive.

        Args:
            v: The monetary amount to validate

        Returns:
            The validated amount

        Raises:
            ValueError: If the amount is not positive
        """
        if v is not None and v <= 0:
            raise ValueError(f"Amount must be positive. Got: {v}")
        return v

    @field_validator("length")
    @classmethod
    def validate_length(cls, v: Optional[int]) -> Optional[int]:
        """Validate film length is positive.

        Args:
            v: The film length value to validate

        Returns:
            The validated film length

        Raises:
            ValueError: If the length is not positive
        """
        if v is not None and v <= 0:
            raise ValueError(f"Film length must be positive. Got: {v}")
        return v


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
