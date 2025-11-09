"""Domain module."""

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
