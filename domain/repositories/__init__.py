"""Domain repositories package.

This package contains repository classes implementing the repository pattern
for data access. Repositories encapsulate database operations and provide
a clean interface for the service layer.

Exports:
    FilmRepository - Film data access operations
    RentalRepository - Rental data access operations
    CategoryRepository - Category data access operations
"""

from domain.repositories.film_repository import FilmRepository
from domain.repositories.rental_repository import RentalRepository
from domain.repositories.category_repository import CategoryRepository

__all__ = [
    "FilmRepository",
    "RentalRepository",
    "CategoryRepository",
]

