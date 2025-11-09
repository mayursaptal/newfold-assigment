"""Rental service for business logic.

This module provides the RentalService class which implements business logic
for rental operations. It acts as an intermediary between the API layer and
the repository layer, handling data transformation and business rules.

Example:
    ```python
    from domain.services import RentalService
    from domain.repositories import RentalRepository
    
    service = RentalService(repository)
    rental = await service.create_rental(rental_data)
    ```
"""

from typing import List, Optional
from domain.repositories.rental_repository import RentalRepository
from domain.schemas.rental import RentalCreate, RentalUpdate, RentalRead


class RentalService:
    """Service for rental business logic.
    
    This class contains business logic for rental operations, orchestrating
    repository calls and transforming data between domain models and schemas.
    
    Attributes:
        repository: RentalRepository instance for data access
    """
    
    def __init__(self, repository: RentalRepository):
        """Initialize service with repository.
        
        Args:
            repository: Rental repository instance for data access
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

