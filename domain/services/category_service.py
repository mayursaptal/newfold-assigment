"""Category service for business logic.

This module provides the CategoryService class which implements business logic
for category operations. It acts as an intermediary between the API layer and
the repository layer, handling data transformation.

Example:
    ```python
    from domain.services import CategoryService
    from domain.repositories import CategoryRepository

    service = CategoryService(repository)
    categories = await service.get_categories(skip=0, limit=10)
    ```
"""

from typing import List, Optional
from domain.repositories.category_repository import CategoryRepository
from domain.schemas.category import CategoryRead


class CategoryService:
    """Service for category business logic.

    This class contains business logic for category operations, orchestrating
    repository calls and transforming data between domain models and schemas.
    Categories are read-only in this application.

    Attributes:
        repository: CategoryRepository instance for data access
    """

    def __init__(self, repository: CategoryRepository):
        """Initialize service with repository.

        Args:
            repository: Category repository instance for data access
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
