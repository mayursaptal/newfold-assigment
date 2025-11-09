"""Repository pattern for data access."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, text
from typing import List, Optional
from domain.models import Film, Rental, FilmCreate, FilmUpdate, RentalCreate, RentalUpdate, Category


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
        # Use raw SQL to insert film to avoid SQLModel foreign key resolution issues
        film_data = film.model_dump()
        
        # Build the INSERT query dynamically based on provided fields
        columns = []
        values = []
        params = {}
        
        for key, value in film_data.items():
            if value is not None:
                columns.append(key)
                values.append(f":{key}")
                params[key] = value
        
        # Add streaming_available if not provided (defaults to False)
        if "streaming_available" not in columns:
            columns.append("streaming_available")
            values.append(":streaming_available")
            params["streaming_available"] = film_data.get("streaming_available", False)
        
        sql_query = text(f"""
            INSERT INTO film ({', '.join(columns)})
            VALUES ({', '.join(values)})
            RETURNING film_id as id, title, description, release_year, language_id, 
                     rental_duration, rental_rate, length, replacement_cost, rating, 
                     streaming_available, last_update
        """)
        result = await self.session.execute(sql_query, params)
        await self.session.commit()
        row = result.fetchone()
        if row:
            film_dict = dict(row._mapping)
            # Handle None values for optional fields
            if film_dict.get("description") is None:
                film_dict["description"] = None
            if film_dict.get("release_year") is None:
                film_dict["release_year"] = None
            if film_dict.get("length") is None:
                film_dict["length"] = None
            return Film(**film_dict)
        raise ValueError("Failed to create film")
    
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
        category: Optional[str] = None,
    ) -> List[Film]:
        """
        Get all films with pagination and optional category filter.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            category: Optional category name to filter by
            
        Returns:
            List of film entities
        """
        # Use raw SQL for category filtering to handle joins properly
        if category:
            # SQL query with joins for category filtering
            # Note: Pagila uses film_id, but we map it to id in the model
            sql_query = text("""
                SELECT DISTINCT 
                    film.film_id as id,
                    film.title,
                    film.description,
                    film.release_year,
                    film.language_id,
                    film.rental_duration,
                    film.rental_rate,
                    film.length,
                    film.replacement_cost,
                    film.rating,
                    COALESCE(film.streaming_available, false) as streaming_available,
                    film.last_update
                FROM film
                INNER JOIN film_category ON film.film_id = film_category.film_id
                INNER JOIN category ON film_category.category_id = category.category_id
                WHERE category.name = :category_name
                ORDER BY film.film_id
                LIMIT :limit OFFSET :skip
            """)
            result = await self.session.execute(
                sql_query,
                {"category_name": category, "limit": limit, "skip": skip}
            )
            # Map results to Film objects
            rows = result.fetchall()
            films = []
            for row in rows:
                film_dict = dict(row._mapping)
                # Handle None values for optional fields
                if film_dict.get("description") is None:
                    film_dict["description"] = None
                if film_dict.get("release_year") is None:
                    film_dict["release_year"] = None
                if film_dict.get("length") is None:
                    film_dict["length"] = None
                films.append(Film(**film_dict))
            return films
        else:
            # Simple query without category filter - use raw SQL to match Pagila schema
            sql_query = text("""
                SELECT 
                    film.film_id as id,
                    film.title,
                    film.description,
                    film.release_year,
                    film.language_id,
                    film.rental_duration,
                    film.rental_rate,
                    film.length,
                    film.replacement_cost,
                    film.rating,
                    COALESCE(film.streaming_available, false) as streaming_available,
                    film.last_update
                FROM film
                ORDER BY film.film_id
                LIMIT :limit OFFSET :skip
            """)
            result = await self.session.execute(
                sql_query,
                {"limit": limit, "skip": skip}
            )
            rows = result.fetchall()
            films = []
            for row in rows:
                film_dict = dict(row._mapping)
                # Handle None values for optional fields
                if film_dict.get("description") is None:
                    film_dict["description"] = None
                if film_dict.get("release_year") is None:
                    film_dict["release_year"] = None
                if film_dict.get("length") is None:
                    film_dict["length"] = None
                films.append(Film(**film_dict))
            return films
    
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
        
        # Use raw SQL to avoid SQLModel type issues with mpaa_rating enum
        set_clauses = []
        params = {"film_id": film_id}
        param_num = 1
        
        for key, value in update_data.items():
            if key == "rating" and value is not None:
                # Cast rating to mpaa_rating enum type
                # Handle both enum objects and string values
                if hasattr(value, 'value'):
                    rating_str = value.value  # Extract value from enum
                else:
                    rating_str = str(value)
                # Validate rating value to prevent SQL injection
                valid_ratings = ["G", "PG", "PG-13", "R", "NC-17"]
                if rating_str not in valid_ratings:
                    raise ValueError(f"Invalid rating: {rating_str}")
                # Use parameter with CAST - asyncpg will handle the parameter binding
                param_key = f"rating_val"
                set_clauses.append(f"rating = CAST(:{param_key} AS mpaa_rating)")
                params[param_key] = rating_str
            elif key == "release_year" and value is not None:
                # Handle release_year - validate against year domain constraint (1901-2155)
                if value == 0:
                    # Skip invalid year (0) - don't update it
                    continue
                if not (1901 <= value <= 2155):
                    raise ValueError(f"release_year must be between 1901 and 2155, got {value}")
                set_clauses.append(f"{key} = :{key}")
                params[key] = value
            elif value is not None:
                set_clauses.append(f"{key} = :{key}")
                params[key] = value
        
        if not set_clauses:
            return await self.get_by_id(film_id)
        
        # Build the SQL query - text() will convert :param to $N style for asyncpg
        set_clauses_str = ', '.join(set_clauses)
        sql_query = text(f"""
            UPDATE film
            SET {set_clauses_str}, last_update = CURRENT_TIMESTAMP
            WHERE film_id = :film_id
            RETURNING film_id as id, title, description, release_year, language_id,
                     rental_duration, rental_rate, length, replacement_cost, rating,
                     streaming_available, last_update
        """)
        
        result = await self.session.execute(sql_query, params)
        await self.session.commit()
        row = result.fetchone()
        if row:
            film_dict = dict(row._mapping)
            # Handle None values for optional fields
            if film_dict.get("description") is None:
                film_dict["description"] = None
            if film_dict.get("release_year") is None:
                film_dict["release_year"] = None
            if film_dict.get("length") is None:
                film_dict["length"] = None
            return Film(**film_dict)
        return None
    
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
    ) -> List[Rental]:
        """
        Get all rentals with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of rental entities
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


class CategoryRepository:
    """Repository for category data access."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: Async database session
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

