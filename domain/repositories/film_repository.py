"""Film repository for database operations.

This module provides the FilmRepository class which implements the repository
pattern for film data access. It handles all database operations for films
including CRUD operations and complex queries with category filtering.

The repository uses raw SQL queries for complex operations to work around
SQLModel's foreign key resolution limitations with the Pagila schema.

Example:
    ```python
    from domain.repositories import FilmRepository
    
    repository = FilmRepository(session)
    film = await repository.create(film_data)
    films = await repository.get_all(skip=0, limit=10, category="Action")
    ```
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
from sqlalchemy.sql import Select, Delete
from typing import List, Optional
from domain.models.film import Film
from domain.schemas.film import FilmCreate, FilmUpdate


class FilmRepository:
    """Repository for film data access operations.
    
    This class encapsulates all database operations for films, providing
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
        
        # Add last_update if not provided (use CURRENT_TIMESTAMP)
        if "last_update" not in columns:
            columns.append("last_update")
            values.append("CURRENT_TIMESTAMP")
        
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
            # Convert last_update string to datetime if needed (for SQLite compatibility)
            if isinstance(film_dict.get("last_update"), str) and film_dict.get("last_update") != "CURRENT_TIMESTAMP":
                from datetime import datetime
                try:
                    film_dict["last_update"] = datetime.fromisoformat(film_dict["last_update"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass
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
        stmt: Select[tuple[Film]] = select(Film).where(Film.id == film_id)
        result = await self.session.execute(stmt)
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
        stmt: Delete = delete(Film).where(Film.id == film_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def search_by_title_with_category(self, title: str) -> Optional[dict]:
        """
        Search for a film by title and return film with category information.
        
        Args:
            title: Film title to search for (case-insensitive partial match)
            
        Returns:
            Dictionary with film info and category, or None if not found
            Format: {
                "title": str,
                "category": str,
                "rental_rate": float,
                "rating": str (optional, MPAA rating)
            }
        """
        # Search for film by title (case-insensitive, partial match) and get category
        sql_query = text("""
            SELECT 
                film.title,
                film.description,
                film.rental_rate,
                film.rating,
                film.release_year,
                category.name as category
            FROM film
            LEFT JOIN film_category ON film.film_id = film_category.film_id
            LEFT JOIN category ON film_category.category_id = category.category_id
            WHERE LOWER(film.title) LIKE LOWER(:title_pattern)
            LIMIT 1
        """)
        result = await self.session.execute(
            sql_query,
            {"title_pattern": f"%{title}%"}
        )
        row = result.fetchone()
        if row:
            return {
                "title": row.title,
                "description": row.description,
                "category": row.category or "Unknown",
                "rental_rate": float(row.rental_rate),
                "rating": str(row.rating) if row.rating else None,
                "release_year": row.release_year
            }
        return None

