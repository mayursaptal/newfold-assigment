"""Rental repository for database operations.

This module provides the RentalRepository class which implements the repository
pattern for rental data access. It handles all database operations for rentals
including CRUD operations and filtering by customer.

The repository uses raw SQL queries for complex operations to work around
SQLModel's foreign key resolution limitations with the Pagila schema.

Example:
    ```python
    from domain.repositories import RentalRepository
    
    repository = RentalRepository(session)
    rental = await repository.create(rental_data)
    rentals = await repository.get_all(skip=0, limit=10, customer_id=1)
    ```
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, delete, text
from typing import List, Optional
from domain.models.rental import Rental
from domain.schemas.rental import RentalCreate, RentalUpdate


class RentalRepository:
    """Repository for rental data access operations.
    
    This class encapsulates all database operations for rentals, providing
    a clean interface for the service layer. It handles raw SQL queries
    for complex operations and type conversions.
    
    Attributes:
        session: Async database session for executing queries
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: Async database session instance
        """
        self.session = session
    
    async def create(self, rental: RentalCreate) -> Rental:
        """
        Create a new rental.
        
        Args:
            rental: Rental creation data
            
        Returns:
            Created rental entity
        """
        from datetime import datetime
        
        # Set rental_date to now() if not provided
        rental_date = rental.rental_date or datetime.utcnow()
        
        # Use raw SQL to insert rental to avoid SQLModel foreign key resolution issues
        sql_query = text("""
            INSERT INTO rental (inventory_id, customer_id, staff_id, rental_date, last_update)
            VALUES (:inventory_id, :customer_id, :staff_id, :rental_date, CURRENT_TIMESTAMP)
            RETURNING rental_id as id, inventory_id, customer_id, staff_id, rental_date, return_date, last_update
        """)
        result = await self.session.execute(
            sql_query,
            {
                "inventory_id": rental.inventory_id,
                "customer_id": rental.customer_id,
                "staff_id": rental.staff_id,
                "rental_date": rental_date,
            }
        )
        await self.session.commit()
        row = result.fetchone()
        if row:
            rental_dict = dict(row._mapping)
            return Rental(**rental_dict)
        raise ValueError("Failed to create rental")
    
    async def get_by_id(self, rental_id: int) -> Optional[Rental]:
        """
        Get rental by ID.
        
        Args:
            rental_id: Rental ID
            
        Returns:
            Rental entity or None
        """
        # Use raw SQL to match Pagila schema
        sql_query = text("""
            SELECT 
                rental.rental_id as id,
                rental.inventory_id,
                rental.customer_id,
                rental.staff_id,
                rental.rental_date,
                rental.return_date,
                rental.last_update
            FROM rental
            WHERE rental.rental_id = :rental_id
        """)
        result = await self.session.execute(
            sql_query,
            {"rental_id": rental_id}
        )
        row = result.fetchone()
        if row:
            rental_dict = dict(row._mapping)
            return Rental(**rental_dict)
        return None
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
    ) -> List[Rental]:
        """
        Get all rentals with pagination and optional customer filter.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            customer_id: Optional customer ID to filter by
            
        Returns:
            List of rental entities
        """
        # Use raw SQL to match Pagila schema
        if customer_id:
            sql_query = text("""
                SELECT 
                    rental.rental_id as id,
                    rental.inventory_id,
                    rental.customer_id,
                    rental.staff_id,
                    rental.rental_date,
                    rental.return_date,
                    rental.last_update
                FROM rental
                WHERE rental.customer_id = :customer_id
                ORDER BY rental.rental_id DESC
                LIMIT :limit OFFSET :skip
            """)
            result = await self.session.execute(
                sql_query,
                {"customer_id": customer_id, "limit": limit, "skip": skip}
            )
        else:
            sql_query = text("""
                SELECT 
                    rental.rental_id as id,
                    rental.inventory_id,
                    rental.customer_id,
                    rental.staff_id,
                    rental.rental_date,
                    rental.return_date,
                    rental.last_update
                FROM rental
                ORDER BY rental.rental_id
                LIMIT :limit OFFSET :skip
            """)
            result = await self.session.execute(
                sql_query,
                {"limit": limit, "skip": skip}
            )
        rows = result.fetchall()
        rentals = []
        for row in rows:
            rental_dict = dict(row._mapping)
            rentals.append(Rental(**rental_dict))
        return rentals
    
    async def update(self, rental_id: int, rental_update: RentalUpdate) -> Optional[Rental]:
        """
        Update a rental.
        
        Args:
            rental_id: Rental ID
            rental_update: Rental update data
            
        Returns:
            Updated rental entity or None
        """
        update_data = rental_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(rental_id)
        
        await self.session.execute(
            update(Rental)
            .where(Rental.id == rental_id)
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_id(rental_id)
    
    async def delete(self, rental_id: int) -> bool:
        """
        Delete a rental.
        
        Args:
            rental_id: Rental ID
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.session.execute(
            delete(Rental).where(Rental.id == rental_id)
        )
        await self.session.commit()
        return result.rowcount > 0

