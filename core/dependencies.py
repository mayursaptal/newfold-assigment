"""Dependency injection functions for FastAPI.

This module provides FastAPI dependency functions for dependency injection.
It includes dependencies for database sessions, repositories, services,
and AI kernel instances. These dependencies are automatically injected
into route handlers using FastAPI's Depends() mechanism.

Example:
    ```python
    from fastapi import Depends
    from core.dependencies import get_film_service
    
    @router.get("/films")
    async def get_films(service: FilmService = Depends(get_film_service)):
        return await service.get_films()
    ```
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from semantic_kernel import Kernel
from core.db import get_async_session
from core.ai_kernel import get_default_kernel
from core.settings import settings, Settings
from domain.repositories import FilmRepository, RentalRepository, CategoryRepository
from domain.services import FilmService, RentalService, AIService, CategoryService


# Database dependencies
async def get_db_session() -> AsyncSession:
    """
    Get async database session.
    
    Yields:
        AsyncSession: Database session
    """
    async for session in get_async_session():
        yield session


# Settings dependency
def get_settings() -> Settings:
    """Get application settings."""
    return settings


# Repository dependencies
def get_film_repository(
    session: AsyncSession = Depends(get_db_session),
) -> FilmRepository:
    """
    Get film repository instance.
    
    Args:
        session: Database session
        
    Returns:
        FilmRepository instance
    """
    return FilmRepository(session)


def get_rental_repository(
    session: AsyncSession = Depends(get_db_session),
) -> RentalRepository:
    """
    Get rental repository instance.
    
    Args:
        session: Database session
        
    Returns:
        RentalRepository instance
    """
    return RentalRepository(session)


def get_category_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CategoryRepository:
    """
    Get category repository instance.
    
    Args:
        session: Database session
        
    Returns:
        CategoryRepository instance
    """
    return CategoryRepository(session)


# Service dependencies
def get_film_service(
    repository: FilmRepository = Depends(get_film_repository),
) -> FilmService:
    """
    Get film service instance.
    
    Args:
        repository: Film repository
        
    Returns:
        FilmService instance
    """
    return FilmService(repository)


def get_rental_service(
    repository: RentalRepository = Depends(get_rental_repository),
) -> RentalService:
    """
    Get rental service instance.
    
    Args:
        repository: Rental repository
        
    Returns:
        RentalService instance
    """
    return RentalService(repository)


def get_category_service(
    repository: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    """
    Get category service instance.
    
    Args:
        repository: Category repository
        
    Returns:
        CategoryService instance
    """
    return CategoryService(repository)


# AI Kernel dependency
def get_ai_kernel() -> Kernel:
    """
    Get Semantic Kernel instance.
    
    Returns:
        Kernel instance
    """
    return get_default_kernel()


# AI Service dependency
def get_ai_service(
    kernel: Kernel = Depends(get_ai_kernel),
) -> AIService:
    """
    Get AI service instance.
    
    Args:
        kernel: Semantic Kernel instance
        
    Returns:
        AIService instance
    """
    return AIService(kernel)

