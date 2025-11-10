"""HandoffOrchestration for routing questions to appropriate agents.

This module uses Semantic Kernel's HandoffOrchestration to route questions
between SearchAgent and LLMAgent based on OrchestrationHandoffs configuration.
"""

from semantic_kernel import Kernel
from semantic_kernel.agents import HandoffOrchestration as SKHandoffOrchestration, OrchestrationHandoffs
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.contents import ChatMessageContent, AuthorRole
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.search_agent import SearchAgent
from app.agents.llm_agent import LLMAgent
from domain.repositories.film_repository import FilmRepository
from core.logging import get_logger


def create_handoff_orchestration(session: AsyncSession, kernel: Kernel) -> tuple[SKHandoffOrchestration, dict]:
    """Create a HandoffOrchestration instance following Microsoft documentation pattern.
    
    Creates SearchAgent and LLMAgent, configures handoffs, and returns
    a Semantic Kernel HandoffOrchestration instance along with a tracking dict
    to capture the last agent name.
    
    Args:
        session: Database session for SearchAgent's repository
        kernel: Semantic Kernel instance for both agents
        
    Returns:
        Tuple of (HandoffOrchestration instance, tracking dict with 'last_agent' key)
    """
    logger = get_logger("ai")  # Use "ai" logger for file logging
    
    # Create repository and agents
    film_repository = FilmRepository(session)
    search_agent_wrapper = SearchAgent(film_repository, kernel=kernel)
    llm_agent_wrapper = LLMAgent(kernel)
    
    # Extract the underlying ChatCompletionAgent instances
    search_agent = search_agent_wrapper.agent
    llm_agent = llm_agent_wrapper.agent
    
    # Build OrchestrationHandoffs configuration following Microsoft pattern
    # Make handoff descriptions very explicit so agents know when to hand off
    # SearchAgent can hand off to LLMAgent, but LLMAgent should NOT hand off back to SearchAgent
    handoffs = (
        OrchestrationHandoffs()
        .add(
            source_agent=search_agent.name,
            target_agent=llm_agent.name,
            description=(
                "ONLY transfer to LLMAgent if ANY of these conditions are true: "
                "(1) The user's question is NOT about a film, movie, or cinema (e.g., personal questions, general knowledge, other topics), "
                "(2) The search_film function returns None/null/empty, "
                "(3) No film match is found in the database. "
                "\n\n"
                "DO NOT transfer to LLMAgent if you successfully found and provided film information. "
                "When you find a film and provide its details, END the conversation - do not hand off. "
                "Only hand off when you cannot handle the request yourself."
            )
        )
        .add(
            source_agent=llm_agent.name,
            target_agent=search_agent.name,
            description=(
                "DO NOT transfer to SearchAgent. "
                "LLMAgent should ANSWER QUESTIONS directly and conversationally. "
                "Simply answer the user's question directly, no matter what it is."
            )
        )
    )
    
    # Track last agent name and conversation state in a dict (mutable, accessible from callbacks)
    agent_tracker = {
        "last_agent": search_agent.name,
        "response_received": False,
        "human_response_calls": 0,
        "last_agent_response": None,  # Store the actual agent response content
        "should_stop": False  # Flag to signal orchestration should stop
    }
    
    # Create response callback to track agent responses and last agent
    async def agent_response_callback(message: ChatMessageContent) -> None:
        """Callback to log agent responses and track last agent."""
        agent_name = message.name or "Unknown"
        previous_agent = agent_tracker.get("last_agent", "Unknown")
        agent_tracker["last_agent"] = agent_name
        
        # Extract content from message - try multiple ways
        content = None
        
        # First try direct content attribute
        if hasattr(message, 'content') and message.content:
            content = str(message.content).strip()
        
        # Try text attribute
        if not content and hasattr(message, 'text') and message.text:
            content = str(message.text).strip()
        
        # Try items attribute (ChatMessageContent may have items)
        if not content:
            items = None
            if hasattr(message, 'items'):
                items = message.items
            elif hasattr(message, '__getitem__') and hasattr(message, '__contains__'):
                # Try to access as dict/list
                try:
                    if 'items' in message:
                        items = message['items']  # type: ignore
                except (TypeError, KeyError):
                    pass
            
            if items:
                # Handle both list and iterable
                try:
                    for item in items:
                        if hasattr(item, 'text') and item.text:
                            content = str(item.text).strip()
                            break
                        elif hasattr(item, 'content') and item.content:
                            content = str(item.content).strip()
                            break
                        elif isinstance(item, dict) and 'text' in item:
                            content = str(item['text']).strip()
                            break
                        elif isinstance(item, dict) and 'content' in item:
                            content = str(item['content']).strip()
                            break
                except (TypeError, AttributeError):
                    pass
        
        # Store the actual agent response content (only for assistant role messages with content)
        role_is_assistant = (
            (hasattr(message, 'role') and
             (hasattr(message.role, 'value') and message.role.value == "assistant" or str(message.role) == "assistant"))
        )
        
        if (role_is_assistant and
            content and
            content.strip() and
            not content.startswith("Task is completed") and
            not content.startswith("__CONVERSATION_COMPLETE__") and
            not content.startswith("Handoff-") and
            not "Handoff-complete_task" in content):
            
            # Only store the FIRST valid response - don't overwrite if we already have one
            if not agent_tracker.get("last_agent_response"):
                agent_tracker["last_agent_response"] = content
                agent_tracker["response_received"] = True  # Mark that we've received a valid response
                agent_tracker["should_stop"] = True  # Signal that orchestration should stop
                
                logger.info(
                    "Stored agent response in tracker",
                    agent_name=agent_name,
                    content_length=len(content),
                    content_preview=content[:200]
                )
            else:
                logger.info(
                    "Ignoring additional agent response (already have first response)",
                    agent_name=agent_name,
                    content_length=len(content),
                    content_preview=content[:200]
                )
        
        # Log handoff if agent changed
        if previous_agent != agent_name:
            logger.info(
                "Agent handoff",
                from_agent=previous_agent,
                to_agent=agent_name,
                message_content=content[:500] if content else ""
            )
        
        # Log agent response with extracted content and debug info
        message_attrs = [attr for attr in dir(message) if not attr.startswith('_')]
        logger.info(
            "Agent response",
            agent_name=agent_name,
            role=message.role.value if hasattr(message.role, 'value') else str(message.role),
            content_length=len(content) if content else 0,
            content_preview=content[:500] if content else "",
            has_content=bool(content),
            message_has_content=bool(hasattr(message, 'content') and message.content),
            message_has_text=bool(hasattr(message, 'text') and message.text),
            message_has_items=bool(hasattr(message, 'items')),
            message_type=type(message).__name__,
            message_attrs_sample=message_attrs[:10] if message_attrs else []
        )
        
        # If no content extracted, try to get it from message directly
        if not content and hasattr(message, '__dict__'):
            logger.warning(
                "No content extracted, checking message __dict__",
                message_dict_keys=list(message.__dict__.keys())[:10] if hasattr(message, '__dict__') else []
            )
    
    # Create human response function for orchestration
    def human_response_function() -> ChatMessageContent:
        """Human response function for orchestration.
        
        In API context, the initial question is provided via the 'task' parameter.
        This function should NOT be called repeatedly after agents provide responses.
        """
        call_count: int = agent_tracker.get("human_response_calls", 0)
        agent_tracker["human_response_calls"] = call_count + 1
        
        logger.debug(
            "Human response function called",
            call_count=call_count + 1
        )
        
        # After the first call, we should not provide more input
        # The orchestration should terminate after agents provide their responses
        if call_count > 0:
            logger.warning(
                "Human response function called multiple times - orchestration should have terminated",
                call_count=call_count + 1
            )
            # Return a special termination signal
            return ChatMessageContent(role=AuthorRole.USER, content="__TERMINATE_CONVERSATION__")
        
        # First call - return empty to let orchestration use the 'task' parameter
        return ChatMessageContent(role=AuthorRole.USER, content="")
    
    # Create HandoffOrchestration following Microsoft documentation pattern
    # Put SearchAgent first in members list as it's the front-desk agent
    orchestration = SKHandoffOrchestration(
        members=[search_agent, llm_agent],  # First agent is typically the starting agent
        handoffs=handoffs,
        agent_response_callback=agent_response_callback,
        human_response_function=human_response_function,
    )
    
    logger.info(
        "HandoffOrchestration created",
        agents=[search_agent.name, llm_agent.name],
        starting_agent=search_agent.name,
        handoff_rules={
            f"{search_agent.name} -> {llm_agent.name}": "Film not found or non-film question",
            f"{llm_agent.name} -> {search_agent.name}": "DO NOT transfer (LLMAgent handles directly)"
        }
    )
    
    return orchestration, agent_tracker
