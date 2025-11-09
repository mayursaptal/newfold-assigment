"""AI Agents package.

This package contains the implementation of various AI agents and
their orchestration logic using Semantic Kernel's HandoffOrchestration.

Modules:
    - `search_agent`: Agent for searching film information in the database.
    - `llm_agent`: Agent for general question answering using an LLM.
    - `orchestration`: Factory function to create HandoffOrchestration instances.
"""

from .search_agent import SearchAgent
from .llm_agent import LLMAgent
from .orchestration import create_handoff_orchestration

__all__ = ["SearchAgent", "LLMAgent", "create_handoff_orchestration"]
