"""Domain models (entities) package.

This package contains SQLModel entity definitions representing database tables.
Models are organized by domain entity (film, rental, category) with base
classes for shared attributes.

Exports:
    Film, FilmBase, FilmRating - Film-related models
    Rental, RentalBase - Rental-related models
    Category, CategoryBase - Category-related models
"""

from domain.models.film import Film, FilmBase, FilmRating
from domain.models.rental import Rental, RentalBase
from domain.models.category import Category, CategoryBase

__all__ = [
    "Film",
    "FilmBase",
    "FilmRating",
    "Rental",
    "RentalBase",
    "Category",
    "CategoryBase",
]

