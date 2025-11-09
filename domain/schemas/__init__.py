"""Domain schemas (Create, Update, Read) package.

This package contains Pydantic schemas for API request/response validation.
Schemas are organized by domain entity and operation type (Create, Update, Read).

Exports:
    Film schemas: FilmCreate, FilmUpdate, FilmRead, FilmSummaryRequest, FilmSummaryResponse
    Rental schemas: RentalCreate, RentalCreateRequest, RentalUpdate, RentalRead
    Category schemas: CategoryRead
    Handoff schemas: HandoffRequest, HandoffResponse
"""

from domain.schemas.film import (
    FilmCreate,
    FilmUpdate,
    FilmRead,
    FilmSummaryRequest,
    FilmSummaryResponse,
)
from domain.schemas.rental import (
    RentalCreate,
    RentalCreateRequest,
    RentalUpdate,
    RentalRead,
)
from domain.schemas.category import CategoryRead
from domain.schemas.handoff import HandoffRequest, HandoffResponse

__all__ = [
    "FilmCreate",
    "FilmUpdate",
    "FilmRead",
    "FilmSummaryRequest",
    "FilmSummaryResponse",
    "RentalCreate",
    "RentalCreateRequest",
    "RentalUpdate",
    "RentalRead",
    "CategoryRead",
    "HandoffRequest",
    "HandoffResponse",
]

