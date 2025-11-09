"""Plugin for film search functionality.

This plugin provides kernel functions for searching films in the database.
It is used by the SearchAgent to handle film-related queries.
"""

from semantic_kernel.functions import kernel_function
from domain.repositories.film_repository import FilmRepository
from core.logging import get_logger


class FilmSearchPlugin:
    """Plugin for searching films in the database.
    
    This plugin provides functions that can be used by Semantic Kernel agents
    to search for film information in the PostgreSQL database.
    
    Attributes:
        repository: FilmRepository instance for database access
        logger: Logger instance for this plugin
    """
    
    def __init__(self, repository: FilmRepository):
        """Initialize FilmSearchPlugin with repository.
        
        Args:
            repository: FilmRepository instance for database access
        """
        self.repository = repository
        self.logger = get_logger(__name__)
    
    @kernel_function(
        name="search_film",
        description="Search for a film by title and return its rental rate and category. Use this when the user asks about a specific film's rental information."
    )
    async def search_film(self, film_title: str) -> str:
        """
        Search for a film by title and return rental information.
        
        Args:
            film_title: Title of the film to search for
            
        Returns:
            Formatted string with film title, category, and rental rate,
            or a message indicating the film was not found
        """
        self.logger.info("FilmSearchPlugin searching for film", film_title=film_title)
        
        # Search database for film
        film_info = await self.repository.search_by_title_with_category(film_title)
        
        if not film_info:
            self.logger.info("Film not found in database", film_title=film_title)
            return f"Film '{film_title}' not found in the database."
        
        # Format answer
        category = film_info["category"]
        rental_rate = film_info["rental_rate"]
        title = film_info["title"]
        
        answer = f"{title} ({category}) rents for ${rental_rate:.2f}."
        
        self.logger.info("FilmSearchPlugin found film", 
                        film_title=title, 
                        category=category, 
                        rental_rate=rental_rate)
        
        return answer

