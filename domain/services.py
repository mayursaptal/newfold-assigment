"""Business logic services (use-cases)."""

from typing import List, Optional
from semantic_kernel import Kernel
from domain.models import (
    Film,
    FilmCreate,
    FilmUpdate,
    FilmRead,
    Rental,
    RentalCreate,
    RentalUpdate,
    RentalRead,
    Category,
    CategoryRead,
)
from domain.repositories import FilmRepository, RentalRepository, CategoryRepository


class FilmService:
    """Service for film business logic."""
    
    def __init__(self, repository: FilmRepository):
        """
        Initialize service with repository.
        
        Args:
            repository: Film repository instance
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


class RentalService:
    """Service for rental business logic."""
    
    def __init__(self, repository: RentalRepository):
        """
        Initialize service with repository.
        
        Args:
            repository: Rental repository instance
        """
        self.repository = repository
    
    async def create_rental(self, rental: RentalCreate) -> RentalRead:
        """
        Create a new rental.
        
        Args:
            rental: Rental creation data
            
        Returns:
            Created rental
        """
        db_rental = await self.repository.create(rental)
        return RentalRead.model_validate(db_rental)
    
    async def get_rental(self, rental_id: int) -> Optional[RentalRead]:
        """
        Get rental by ID.
        
        Args:
            rental_id: Rental ID
            
        Returns:
            Rental or None
        """
        rental = await self.repository.get_by_id(rental_id)
        if not rental:
            return None
        return RentalRead.model_validate(rental)
    
    async def get_rentals(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
    ) -> List[RentalRead]:
        """
        Get all rentals with pagination and optional customer filter.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            customer_id: Optional customer ID to filter by
            
        Returns:
            List of rentals
        """
        rentals = await self.repository.get_all(skip=skip, limit=limit, customer_id=customer_id)
        return [RentalRead.model_validate(rental) for rental in rentals]
    
    async def update_rental(
        self,
        rental_id: int,
        rental_update: RentalUpdate,
    ) -> Optional[RentalRead]:
        """
        Update a rental.
        
        Args:
            rental_id: Rental ID
            rental_update: Rental update data
            
        Returns:
            Updated rental or None
        """
        rental = await self.repository.update(rental_id, rental_update)
        if not rental:
            return None
        return RentalRead.model_validate(rental)
    
    async def delete_rental(self, rental_id: int) -> bool:
        """
        Delete a rental.
        
        Args:
            rental_id: Rental ID
            
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(rental_id)


class AIService:
    """Service for AI/Semantic Kernel operations."""
    
    def __init__(self, kernel: Kernel):
        """
        Initialize service with Semantic Kernel.
        
        Args:
            kernel: Semantic Kernel instance
        """
        self.kernel = kernel
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate text using Semantic Kernel.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        # This is a placeholder - actual implementation depends on SK version
        # You would use kernel.invoke() or similar method
        try:
            # Example: invoke a function from the kernel
            # result = await self.kernel.invoke(prompt_function, input=prompt)
            # return str(result)
            return f"AI response to: {prompt}"
        except Exception as e:
            raise ValueError(f"AI generation failed: {str(e)}")
    
    async def chat_completion(
        self,
        messages: List[dict],
        temperature: float = 0.7,
    ) -> str:
        """
        Chat completion using Semantic Kernel.
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            
        Returns:
            Chat response
        """
        # Placeholder implementation
        # Actual implementation would use kernel's chat completion
        return "AI chat response"


class CategoryService:
    """Service for category business logic."""
    
    def __init__(self, repository: CategoryRepository):
        """
        Initialize service with repository.
        
        Args:
            repository: Category repository instance
        """
        self.repository = repository
    
    async def get_categories(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CategoryRead]:
        """
        Get all categories with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of categories
        """
        categories = await self.repository.get_all(skip=skip, limit=limit)
        return [CategoryRead.model_validate(category) for category in categories]
    
    async def get_category(self, category_id: int) -> Optional[CategoryRead]:
        """
        Get category by ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category or None
        """
        category = await self.repository.get_by_id(category_id)
        if not category:
            return None
        return CategoryRead.model_validate(category)

