"""AI Agents package.

This package contains the implementation of various AI agents and
their orchestration logic using OrchestrationHandoffs configuration pattern.

Modules:
    - `search_agent`: Agent for searching film information in the database.
    - `llm_agent`: Agent for general question answering using an LLM.
    - `orchestration`: HandoffOrchestration with custom routing logic.
"""

from .search_agent import SearchAgent
from .llm_agent import LLMAgent
from .orchestration import HandoffOrchestration

__all__ = ["SearchAgent", "LLMAgent", "HandoffOrchestration"]
