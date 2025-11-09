"""SearchAgent for film-related questions.

This agent examines the user's question, fetches matching film information
from PostgreSQL, and generates a short summary of the movie using AI.
"""

import re
from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from domain.repositories.film_repository import FilmRepository
from core.logging import get_logger
from core.plugin_loader import get_plugin_function


class SearchAgent:
    """Agent that searches for film information in the database.
    
    This agent handles questions about films by querying the PostgreSQL database
    to find matching films and their categories, then formats a response with
    rental rate information.
    
    Attributes:
        repository: FilmRepository instance for database access
        kernel: Semantic Kernel instance (required for HandoffOrchestration)
        logger: Logger instance for this agent
        name: Agent name for orchestration (required for OrchestrationHandoffs)
        description: Agent description (required for HandoffOrchestration)
    """
    
    def __init__(self, repository: FilmRepository, kernel: Kernel = None):
        """Initialize SearchAgent with repository and kernel.
        
        Args:
            repository: FilmRepository instance for database access
            kernel: Optional Semantic Kernel instance (required for HandoffOrchestration)
                   If not provided, creates a minimal kernel
        """
        self.repository = repository
        self.logger = get_logger(__name__)
        self.name = "SearchAgent"  # Required for OrchestrationHandoffs
        self.description = "A customer support agent that searches for film information in the database and generates short summaries of movies."
        
        # Create a minimal kernel if not provided (required for HandoffOrchestration)
        if kernel is None:
            from semantic_kernel import Kernel
            kernel = Kernel()
        self.kernel = kernel
    
    async def _generate_film_summary(self, film_info: dict) -> str:
        """
        Generate a short summary of the film using AI.
        
        Args:
            film_info: Dictionary with film information
            
        Returns:
            Short summary string (2-3 sentences)
        """
        try:
            # Get short summary function (auto-registered at kernel initialization)
            summary_function = get_plugin_function(
                self.kernel,
                plugin_name="film_short_summary",
                function_name="generate_summary"
            )
            
            # Prepare film info text
            film_info_text = f"""Title: {film_info['title']}
Category: {film_info['category']}
Rating: {film_info.get('rating', 'N/A')}
Release Year: {film_info.get('release_year', 'N/A')}
Description: {film_info.get('description', 'No description available')}"""
            
            # Invoke summary function
            arguments = KernelArguments(film_info=film_info_text)
            response = await self.kernel.invoke(
                function=summary_function,
                arguments=arguments
            )
            
            # Extract response content
            summary = ""
            if hasattr(response, 'value'):
                response_value = response.value
                
                # Handle list responses
                if isinstance(response_value, list):
                    for item in response_value:
                        if hasattr(item, 'content') and item.content:
                            summary = str(item.content)
                            break
                        elif hasattr(item, 'inner_content'):
                            inner = item.inner_content
                            if hasattr(inner, 'choices') and inner.choices:
                                choice = inner.choices[0]
                                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                                    summary = str(choice.message.content)
                                    break
                # Handle single object
                else:
                    if hasattr(response_value, 'content') and response_value.content:
                        summary = str(response_value.content)
                    elif hasattr(response_value, 'inner_content'):
                        inner = response_value.inner_content
                        if hasattr(inner, 'choices') and inner.choices:
                            choice = inner.choices[0]
                            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                                summary = str(choice.message.content)
            
            # Clean up summary
            summary = summary.strip()
            
            # Remove markdown code blocks if present
            if summary.startswith("```"):
                lines = summary.split('\n')
                summary = '\n'.join(lines[1:-1]) if len(lines) > 2 else summary
            
            return summary
                
        except Exception as e:
            self.logger.error("Failed to generate AI summary",
                              error=str(e),
                              error_type=type(e).__name__)
            raise
    
    async def process(self, question: str) -> str:
        """
        Process a question and return an answer about film rental rates.
        
        Extracts film title from the question and searches the database.
        Returns a formatted answer with film title, category, and rental rate.
        
        Args:
            question: User's question (should contain a film title)
            
        Returns:
            Formatted answer string, e.g., "Alien (Horror) rents for $2.99."
        """
        self.logger.info("SearchAgent processing question", question=question[:100])
        
        # Extract potential film title from question
        # Improved approach: handle titles at start, after "film"/"movie", or in quotes
        film_title = None
        
        # Try to find film title - look for quoted text first
        quoted_match = re.search(r'"([^"]+)"', question)
        if quoted_match:
            film_title = quoted_match.group(1)
        
        # Look for pattern: "film X" or "movie X" (case-insensitive, more flexible)
        if not film_title:
            # Match text after "film" or "movie" until end, punctuation, or common words
            film_pattern = re.search(r'(?:film|movie)\s+([A-Z][a-zA-Z\s]+?)(?:\?|\.|$|,|!|;|:|\s+(?:rental|rate|is|the|what|about))', question, re.IGNORECASE)
            if film_pattern:
                film_title = film_pattern.group(1).strip()
        
        # Look for capitalized words at the START of the question (title might come first)
        if not film_title:
            words = question.split()
            title_words = []
            skip_words = {"what", "is", "the", "rental", "rate", "for", "film", "movie", "of", "a", "an", "about", "tell", "me", "this", "that"}
            
            # Check if question starts with capitalized words (likely a film title)
            for i, word in enumerate(words):
                word_clean = word.rstrip('.,!?;:')
                # If we're at the start and see capitalized words, collect them
                if i < 5 and word_clean and word_clean[0].isupper():
                    if word_clean.lower() not in skip_words:
                        title_words.append(word_clean)
                    elif title_words:
                        # Stop if we hit a skip word after collecting title words
                        break
                elif title_words:
                    # Continue if next word is also capitalized (multi-word title)
                    if word_clean and word_clean[0].isupper() and word_clean.lower() not in skip_words:
                        title_words.append(word_clean)
                    else:
                        # Stop if we hit a non-capitalized word or skip word
                        break
            
            if title_words:
                film_title = " ".join(title_words)
        
        # Look for capitalized words anywhere in question (potential film title)
        if not film_title:
            words = question.split()
            title_words = []
            skip_words = {"what", "is", "the", "rental", "rate", "for", "film", "movie", "of", "a", "an", "about", "tell", "me", "this", "that", "of", "this", "movie"}
            
            for word in words:
                word_clean = word.rstrip('.,!?;:')
                # Skip common question words
                if word_clean.lower() in skip_words:
                    continue
                # Check for capitalized word
                if word_clean and word_clean[0].isupper():
                    title_words.append(word_clean)
                elif title_words and word_clean:
                    # Stop if we hit a non-capitalized word after finding title words
                    if word_clean.lower() not in skip_words:
                        break
            
            if title_words:
                film_title = " ".join(title_words)
        
        # Handle single capitalized word (might be a film title)
        if not film_title:
            words = question.split()
            skip_words = {"what", "is", "the", "rental", "rate", "for", "film", "movie", "of", "a", "an", "about", "tell", "me", "i", "you", "can", "help", "this", "that"}
            for word in words:
                word_clean = word.rstrip('.,!?;:')
                if (word_clean and word_clean[0].isupper() and 
                    word_clean.lower() not in skip_words and
                    len(word_clean) > 2):  # Skip very short words
                    film_title = word_clean
                    break
        
        if not film_title:
            self.logger.warning("Could not extract film title from question", question=question)
            return None
        
        # Search database for film
        film_info = await self.repository.search_by_title_with_category(film_title)
        
        if not film_info:
            self.logger.info("Film not found in database", film_title=film_title)
            return None
        
        # Determine what the user is asking for
        question_lower = question.lower()
        
        # Check for specific information requests
        if "rating" in question_lower or "rated" in question_lower:
            # Question is about rating - only return rating
            rating = film_info.get("rating")
            if rating:
                return f"{film_info['title']} is rated {rating}."
            else:
                return f"{film_info['title']} does not have a rating available."
        elif "rental" in question_lower or ("rate" in question_lower and "rental" in question_lower) or "cost" in question_lower or "price" in question_lower:
            # Question is about rental rate - only return rental rate
            return f"{film_info['title']} rents for ${film_info['rental_rate']:.2f}."
        elif "category" in question_lower:
            # Question is about category - only return category
            return f"{film_info['title']} is in the {film_info['category']} category."
        else:
            # Default: Generate a short summary of the movie
            summary = await self._generate_film_summary(film_info)
            
            self.logger.info("SearchAgent generated film summary", 
                            film_title=film_info['title'], 
                            category=film_info['category'],
                            summary_length=len(summary))
            
            return summary

