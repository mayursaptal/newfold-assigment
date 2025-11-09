"""Film search native function plugin.

This plugin provides native Python functions for searching films in the database.
These functions can be used as tools by Semantic Kernel agents.
"""

from .film_search_plugin import FilmSearchPlugin

__all__ = ["FilmSearchPlugin"]

