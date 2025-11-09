"""Category service."""

from typing import List, Optional
from domain.repositories.category_repository import CategoryRepository
from domain.schemas.category import CategoryRead


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

