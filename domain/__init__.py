"""Domain module package.

This package contains the domain layer with models, schemas, repositories,
and services. It provides a clean interface for business logic and data
access, independent of the API layer.

The domain layer follows the repository pattern and service layer pattern
for separation of concerns. All domain logic is infrastructure-agnostic.

Exports:
    Models: Film, Rental, Category and their base classes
    Schemas: Pydantic schemas for API validation
    Repositories: Data access layer
    Services: Business logic layer
"""

# Re-export for backward compatibility
from domain.models import Film, FilmBase, FilmRating, Rental, RentalBase, Category, CategoryBase
from domain.schemas import FilmCreate, FilmUpdate, FilmRead, RentalCreate, RentalUpdate, RentalRead, CategoryRead
from domain.repositories import FilmRepository, RentalRepository, CategoryRepository
from domain.services import FilmService, RentalService, CategoryService, AIService

__all__ = [
    # Models
    "Film",
    "FilmBase",
    "FilmRating",
    "Rental",
    "RentalBase",
    "Category",
    "CategoryBase",
    # Schemas
    "FilmCreate",
    "FilmUpdate",
    "FilmRead",
    "RentalCreate",
    "RentalUpdate",
    "RentalRead",
    "CategoryRead",
    # Repositories
    "FilmRepository",
    "RentalRepository",
    "CategoryRepository",
    # Services
    "FilmService",
    "RentalService",
    "CategoryService",
    "AIService",
]
