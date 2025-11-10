"""Film search plugin package.

This package contains the FilmSearchPlugin which provides native function
plugins for searching films in the database using Semantic Kernel.

The FilmSearchPlugin exposes database query functions as tools that Semantic Kernel
agents can use to fetch film information. This allows AI agents to search for
films by title and retrieve detailed information including category, rating,
rental rate, and description.

Example:
    ```python
    from plugins.film_search import FilmSearchPlugin
    from domain.repositories import FilmRepository
    
    # Create plugin with repository
    plugin = FilmSearchPlugin(repository)
    
    # Register with kernel
    kernel.add_plugin(plugin, "film_search")
    
    # Agent can now use search_film function
    ```

Functions:
    search_film: Search for a film by title in the database
"""

from .film_search_plugin import FilmSearchPlugin

__all__ = ["FilmSearchPlugin"]

