"""HandoffOrchestration for routing questions to appropriate agents.

This module implements the orchestration logic using Semantic Kernel's
OrchestrationHandoffs configuration pattern, but with a custom process()
method that works with our custom agent classes.

While we use OrchestrationHandoffs for configuration (following Microsoft
documentation pattern), we implement custom routing logic since our agents
don't inherit from Semantic Kernel's Agent base class.
"""

from semantic_kernel.agents import OrchestrationHandoffs
from app.agents.search_agent import SearchAgent
from app.agents.llm_agent import LLMAgent
from core.logging import get_logger


class HandoffOrchestration:
    """Orchestrates routing between SearchAgent and LLMAgent.
    
    This class uses OrchestrationHandoffs for configuration (following
    Microsoft documentation pattern), but implements custom routing logic
    using our agents' process() methods since they don't inherit from
    Semantic Kernel's Agent base class.
    
    Attributes:
        search_agent: SearchAgent instance for film questions
        llm_agent: LLMAgent instance for general questions
        handoffs: OrchestrationHandoffs configuration (for documentation)
        logger: Logger instance for orchestration
    """
    
    def __init__(self, search_agent: SearchAgent, llm_agent: LLMAgent):
        """Initialize HandoffOrchestration with both agents.
        
        Args:
            search_agent: SearchAgent instance (front-desk agent)
            llm_agent: LLMAgent instance (fallback agent)
        """
        self.search_agent = search_agent
        self.llm_agent = llm_agent
        self.logger = get_logger(__name__)
        
        # Build OrchestrationHandoffs configuration for documentation
        # This follows the Microsoft documentation pattern, even though
        # we use custom routing logic
        self.handoffs = (
            OrchestrationHandoffs()
            .add(
                source_agent=search_agent.name,
                target_agent=llm_agent.name,
                description="Transfer to this agent if the question is not film-related or no film match is found"
            )
            .add(
                source_agent=llm_agent.name,
                target_agent=search_agent.name,
                description="Transfer to this agent if the question is film-related"
            )
        )
    
    async def process(self, question: str) -> dict:
        """
        Process a question and route it to the appropriate agent.
        
        Routing logic:
        1. Always try SearchAgent first if question might be about a film
        2. Check if question contains "film"/"movie" keyword OR has capitalized words (potential film title)
        3. If SearchAgent finds a match, return its answer
        4. If SearchAgent finds no match, hand off to LLMAgent
        5. If question clearly doesn't relate to films, go directly to LLMAgent
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with agent name and answer:
            {"agent": "SearchAgent" | "LLMAgent", "answer": str}
        """
        self.logger.info("HandoffOrchestration processing question", question=question[:100])
        
        question_lower = question.lower()
        contains_film_keyword = "film" in question_lower or "movie" in question_lower
        
        # Check if question might be about a film:
        # - Contains "film"/"movie" keyword, OR
        # - Has capitalized words that might be a film title (at least 2 capitalized words or one long capitalized word)
        import re
        words = question.split()
        capitalized_words = [w for w in words if w and w[0].isupper() and len(w) > 2]
        might_be_film_question = contains_film_keyword or len(capitalized_words) >= 1
        
        # If question might be about a film, try SearchAgent first
        if might_be_film_question:
            self.logger.info("Question might be about a film, trying SearchAgent first")
            answer = await self.search_agent.process(question)
            
            # If SearchAgent found a match, return its answer
            if answer:
                self.logger.info("SearchAgent found match", answer=answer[:100])
                return {
                    "agent": "SearchAgent",
                    "answer": answer
                }
            
            # If no match found, hand off to LLMAgent
            self.logger.info("SearchAgent found no match, handing off to LLMAgent")
            answer = await self.llm_agent.process(question)
            return {
                "agent": "LLMAgent",
                "answer": answer
            }
        
        # If question clearly doesn't relate to films, go directly to LLMAgent
        self.logger.info("Question does not appear to be about films, using LLMAgent")
        answer = await self.llm_agent.process(question)
        return {
            "agent": "LLMAgent",
            "answer": answer
        }
