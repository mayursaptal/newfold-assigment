"""Handoff API schemas.

This module contains Pydantic schemas for agent handoff orchestration endpoints.
"""

from pydantic import BaseModel


class HandoffRequest(BaseModel):
    """Request model for handoff endpoint.

    Attributes:
        question: User's question to be answered
    """

    question: str


class HandoffResponse(BaseModel):
    """Response model for handoff endpoint.

    Attributes:
        agent: Name of the agent that handled the question (SearchAgent or LLMAgent)
        answer: Answer text from the agent
    """

    agent: str
    answer: str
