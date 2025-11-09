"""Category repository for database operations.

This module provides the CategoryRepository class which implements the repository
pattern for category data access. It handles all database operations for categories
including read operations with pagination.

Example:
    ```python
    from domain.repositories import CategoryRepository
    
    repository = CategoryRepository(session)
    categories = await repository.get_all(skip=0, limit=10)
    category = await repository.get_by_id(1)
    ```
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from domain.models.category import Category


class CategoryRepository:
    """Repository for category data access operations.
    
    This class encapsulates all database operations for categories, providing
    a clean interface for the service layer. Categories are read-only in
    this application.
    
    Attributes:
        session: Async database session for executing queries
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: Async database session instance
        """
        self.session = session
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Category]:
        """
        Get all categories with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of category entities
        """
        # Use raw SQL to match Pagila schema
        sql_query = text("""
            SELECT 
                category.category_id as id,
                category.name,
                category.last_update
            FROM category
            ORDER BY category.category_id
            LIMIT :limit OFFSET :skip
        """)
        result = await self.session.execute(
            sql_query,
            {"limit": limit, "skip": skip}
        )
        rows = result.fetchall()
        categories = []
        for row in rows:
            category_dict = dict(row._mapping)
            categories.append(Category(**category_dict))
        return categories
    
    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """
        Get category by ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category entity or None
        """
        sql_query = text("""
            SELECT 
                category.category_id as id,
                category.name,
                category.last_update
            FROM category
            WHERE category.category_id = :category_id
        """)
        result = await self.session.execute(
            sql_query,
            {"category_id": category_id}
        )
        row = result.fetchone()
        if row:
            category_dict = dict(row._mapping)
            return Category(**category_dict)
        return None

