"""SearchAgent for film-related questions.

This agent uses ChatCompletionAgent with native function plugins to let the AI
handle film searches, title extraction, and response formatting automatically.
"""

from typing import Optional
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from domain.repositories.film_repository import FilmRepository
from core.logging import get_logger
from plugins.film_search import FilmSearchPlugin


class SearchAgent:
    """Agent that searches for film information in the database.
    
    This agent uses ChatCompletionAgent with native function plugins to let the AI
    automatically handle film searches, understand questions, and format responses.
    The AI decides when to query the database and how to respond.
    
    Attributes:
        agent: ChatCompletionAgent instance configured with film search and summary plugins
        kernel: Semantic Kernel instance (required for HandoffOrchestration)
        logger: Logger instance for this agent
        name: Agent name for orchestration (required for OrchestrationHandoffs)
        description: Agent description (required for HandoffOrchestration)
    """
    
    def __init__(self, repository: FilmRepository, kernel: Optional[Kernel] = None):
        """Initialize SearchAgent with repository and kernel.
        
        Args:
            repository: FilmRepository instance for database access
            kernel: Optional Semantic Kernel instance (required for HandoffOrchestration)
                   If not provided, creates a minimal kernel
        """
        self.logger = get_logger("ai")  # Use "ai" logger for file logging
        self.name = "SearchAgent"  # Required for OrchestrationHandoffs
        self.description = "A customer support agent that searches for film information in the database and generates short summaries of movies."
        
        # Create a minimal kernel if not provided (required for HandoffOrchestration)
        if kernel is None:
            from semantic_kernel import Kernel
            kernel = Kernel()
        self.kernel = kernel
        
        # Register native function plugin for film search
        film_search_plugin = FilmSearchPlugin(repository)
        kernel.add_plugin(film_search_plugin, "film_search")
        self.logger.info("Registered film_search native function plugin")
        
        # Get other plugins from kernel (already registered)
        plugins = []
        try:
            film_summary_plugin = kernel.get_plugin("film_short_summary")
            if film_summary_plugin:
                plugins.append(film_summary_plugin)
                self.logger.info("Using film_short_summary plugin with ChatCompletionAgent")
        except Exception:
            pass
        
        # Default instructions for the agent - let AI handle everything
        default_instructions = (
            "You are a helpful customer support assistant specializing ONLY in film information. "
            "You ANSWER QUESTIONS about films in a conversational, human-readable way. "
            "\n\nCRITICAL RULES: "
            "1. If the user's question is NOT about a film, movie, or cinema, you MUST IMMEDIATELY request a handoff to LLMAgent. "
            "   Do NOT try to answer non-film questions yourself. Examples of non-film questions: "
            "   - Personal questions (name, age, etc.) "
            "   - General knowledge questions "
            "   - Questions about other topics "
            "2. When users ask about films, use the search_film function from the film_search plugin "
            "   to find information in the database. You can extract film titles from questions automatically. "
            "3. If the search_film function returns None, null, or empty (film not found), "
            "   you MUST IMMEDIATELY request a handoff to LLMAgent with the user's original question. "
            "4. If a film is found, provide a CONVERSATIONAL, HUMAN-READABLE response about the film. "
            "   Example: 'Academy Dinosaur is a fascinating epic drama from 2012. It's rated PG and falls under the Games category. "
            "   The film tells the story of a feminist and a mad scientist who must battle a teacher in The Canadian Rockies. "
            "   You can rent it for $0.99. It's a 86-minute adventure that was released in 2006.' "
            "   DO NOT say 'Task is completed' or provide summaries. Just answer naturally about the film. "
            "5. CRITICAL: After providing film information, you MUST NOT respond again or continue the conversation. "
            "   The conversation should END after your film response. "
            "\n\nRemember: You are having a CONVERSATION, not completing tasks. Answer questions naturally and conversationally."
        )        
        # Create ChatCompletionAgent with all plugins
        self.agent = ChatCompletionAgent(
            kernel=kernel,
            name=self.name,
            instructions=default_instructions,
            arguments=KernelArguments()
        )

