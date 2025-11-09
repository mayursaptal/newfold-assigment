"""Native function plugin for searching films in the database.

This plugin provides native Python functions that can be used by Semantic Kernel
agents to query the film database. The functions are registered as tools that
the agent can call when it needs film information.
"""

from semantic_kernel.functions import kernel_function
from typing import Optional
from domain.repositories.film_repository import FilmRepository


class FilmSearchPlugin:
    """Plugin providing native functions for film database searches.
    
    This plugin exposes database query functions as tools that Semantic Kernel
    agents can use to fetch film information.
    
    Attributes:
        repository: FilmRepository instance for database access
    """
    
    def __init__(self, repository: FilmRepository):
        """Initialize plugin with repository.
        
        Args:
            repository: FilmRepository instance for database access
        """
        self.repository = repository
    
    @kernel_function(
        name="search_film",
        description="Search for a film by title in the database. Returns film information including title, category, rating, rental rate, description, and release year. Use this when the user asks about a specific film. The title parameter can be a partial match - the function will find films with titles containing the search term."
    )
    async def search_film(self, title: str) -> Optional[dict]:
        """
        Search for a film by title in the database.
        
        Args:
            title: Film title to search for (case-insensitive partial match)
            
        Returns:
            Dictionary with film info and category, or None if not found
            Format: {
                "title": str,
                "category": str,
                "rental_rate": float,
                "rating": str (optional, MPAA rating),
                "description": str (optional),
                "release_year": int (optional)
            }
        """
        return await self.repository.search_by_title_with_category(title)

