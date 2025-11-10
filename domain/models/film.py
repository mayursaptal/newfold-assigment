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
from typing import Optional, Any
from sqlmodel import SQLModel, Field
from enum import Enum
from sqlalchemy import Column, Enum as SQLEnum, TypeDecorator
from pydantic import field_validator


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


class FilmRatingType(TypeDecorator):
    """Custom type decorator to handle FilmRating enum with database values.

    This decorator ensures that SQLAlchemy uses enum values (e.g., "NC-17")
    instead of enum names (e.g., "NC17") when mapping to/from the database.
    """

    impl = SQLEnum
    cache_ok = True

    def __init__(self) -> None:
        super().__init__(
            FilmRating,
            values_callable=lambda x: [e.value for e in FilmRating],
            name="mpaa_rating",
            create_constraint=False,
        )

    def process_bind_param(self, value: FilmRating | str | None, dialect: Any) -> str | None:
        """Convert enum to database value."""
        if value is None:
            return None
        if isinstance(value, FilmRating):
            return value.value
        return str(value)

    def process_result_value(self, value: str | None, dialect: Any) -> FilmRating | None:
        """Convert database value to enum."""
        if value is None:
            return None
        # Find enum member by value
        for rating in FilmRating:
            if rating.value == value:
                return rating
        # Fallback: try to create from value directly
        return FilmRating(value) if value in [r.value for r in FilmRating] else None


class FilmBase(SQLModel):
    """Base film model with common attributes.

    This is the base class for Film entities, containing all the common
    film attributes that are shared between create, update, and read operations.

    Attributes:
        title: Film title (indexed for faster searches)
        description: Film description/synopsis
        release_year: Year the film was released (must be between 1901 and 2155)
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
    rating: Optional[FilmRating] = Field(default=None, sa_column=Column(FilmRatingType()))
    streaming_available: bool = Field(default=False)  # Boolean column with default FALSE

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
    def validate_rental_duration(cls, v: int) -> int:
        """Validate rental duration is positive.

        Args:
            v: The rental duration value to validate

        Returns:
            The validated rental duration

        Raises:
            ValueError: If the rental duration is not positive
        """
        if v <= 0:
            raise ValueError(f"Rental duration must be positive. Got: {v}")
        return v

    @field_validator("rental_rate", "replacement_cost")
    @classmethod
    def validate_positive_amount(cls, v: float) -> float:
        """Validate monetary amounts are positive.

        Args:
            v: The monetary amount to validate

        Returns:
            The validated amount

        Raises:
            ValueError: If the amount is not positive
        """
        if v <= 0:
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
        default_factory=datetime.utcnow, sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )
