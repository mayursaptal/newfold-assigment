"""Film service for business logic.

This module provides the FilmService class which implements business logic
for film operations. It acts as an intermediary between the API layer and
the repository layer, handling data transformation and business rules.

Example:
    ```python
    from domain.services import FilmService
    from domain.repositories import FilmRepository
    
    service = FilmService(repository)
    film = await service.create_film(film_data)
    ```
"""

from typing import List, Optional
from domain.repositories.film_repository import FilmRepository
from domain.schemas.film import FilmCreate, FilmUpdate, FilmRead


class FilmService:
    """Service for film business logic.
    
    This class contains business logic for film operations, orchestrating
    repository calls and transforming data between domain models and schemas.
    
    Attributes:
        repository: FilmRepository instance for data access
    """
    
    def __init__(self, repository: FilmRepository):
        """Initialize service with repository.
        
        Args:
            repository: Film repository instance for data access
        """
        self.repository = repository
    
    async def create_film(self, film: FilmCreate) -> FilmRead:
        """
        Create a new film.
        
        Args:
            film: Film creation data
            
        Returns:
            Created film
        """
        db_film = await self.repository.create(film)
        return FilmRead.model_validate(db_film)
    
    async def get_film(self, film_id: int) -> Optional[FilmRead]:
        """
        Get film by ID.
        
        Args:
            film_id: Film ID
            
        Returns:
            Film or None
        """
        film = await self.repository.get_by_id(film_id)
        if not film:
            return None
        return FilmRead.model_validate(film)
    
    async def get_films(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
    ) -> List[FilmRead]:
        """
        Get all films with pagination and optional category filter.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            category: Optional category name to filter by
            
        Returns:
            List of films
        """
        films = await self.repository.get_all(skip=skip, limit=limit, category=category)
        return [FilmRead.model_validate(film) for film in films]
    
    async def update_film(
        self,
        film_id: int,
        film_update: FilmUpdate,
    ) -> Optional[FilmRead]:
        """
        Update a film.
        
        Args:
            film_id: Film ID
            film_update: Film update data
            
        Returns:
            Updated film or None
        """
        film = await self.repository.update(film_id, film_update)
        if not film:
            return None
        return FilmRead.model_validate(film)
    
    async def delete_film(self, film_id: int) -> bool:
        """
        Delete a film.
        
        Args:
            film_id: Film ID
            
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(film_id)

