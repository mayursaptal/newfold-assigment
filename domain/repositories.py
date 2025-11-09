"""Repository pattern for data access."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from domain.models import Film, Rental, FilmCreate, FilmUpdate, RentalCreate, RentalUpdate


class FilmRepository:
    """Repository for film data access."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: Async database session
        """
        self.session = session
    
    async def create(self, film: FilmCreate) -> Film:
        """
        Create a new film.
        
        Args:
            film: Film creation data
            
        Returns:
            Created film entity
        """
        db_film = Film(**film.model_dump())
        self.session.add(db_film)
        await self.session.commit()
        await self.session.refresh(db_film)
        return db_film
    
    async def get_by_id(self, film_id: int) -> Optional[Film]:
        """
        Get film by ID.
        
        Args:
            film_id: Film ID
            
        Returns:
            Film entity or None
        """
        result = await self.session.execute(
            select(Film).where(Film.id == film_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Film]:
        """
        Get all films with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of film entities
        """
        result = await self.session.execute(
            select(Film).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def update(self, film_id: int, film_update: FilmUpdate) -> Optional[Film]:
        """
        Update a film.
        
        Args:
            film_id: Film ID
            film_update: Film update data
            
        Returns:
            Updated film entity or None
        """
        update_data = film_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(film_id)
        
        await self.session.execute(
            update(Film)
            .where(Film.id == film_id)
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_id(film_id)
    
    async def delete(self, film_id: int) -> bool:
        """
        Delete a film.
        
        Args:
            film_id: Film ID
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.session.execute(
            delete(Film).where(Film.id == film_id)
        )
        await self.session.commit()
        return result.rowcount > 0


class RentalRepository:
    """Repository for rental data access."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: Async database session
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
        db_rental = Rental(**rental.model_dump())
        self.session.add(db_rental)
        await self.session.commit()
        await self.session.refresh(db_rental)
        return db_rental
    
    async def get_by_id(self, rental_id: int) -> Optional[Rental]:
        """
        Get rental by ID.
        
        Args:
            rental_id: Rental ID
            
        Returns:
            Rental entity or None
        """
        result = await self.session.execute(
            select(Rental).where(Rental.id == rental_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Rental]:
        """
        Get all rentals with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of rental entities
        """
        result = await self.session.execute(
            select(Rental).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
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

