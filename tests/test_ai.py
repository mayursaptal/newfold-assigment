"""Happy-path tests for AI endpoints.

This module contains one happy-path test per AI endpoint.
AI service methods are mocked to avoid actual API calls.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_ask_question(client: AsyncClient):
    """Happy-path: Ask a question to the AI and get streaming response."""
    with patch("domain.services.ai_service.AIService.stream_chat") as mock_stream:
        async def mock_stream_generator():
            yield "Hello"
            yield " "
            yield "World"
        
        mock_stream.return_value = mock_stream_generator()
        
        response = await client.get("/api/v1/ai/ask?question=hello")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"


@pytest.mark.asyncio
async def test_get_film_summary(client: AsyncClient):
    """Happy-path: Get AI-generated summary for a film."""
    with patch("domain.services.ai_service.AIService.get_film_summary") as mock_summary:
        mock_summary.return_value = {
            "title": "Test Film",
            "rating": "PG-13",
            "recommended": True
        }
        
        request_data = {"film_id": 1}
        response = await client.post("/api/v1/ai/summary", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Film"
        assert data["rating"] == "PG-13"
        assert data["recommended"] is True


@pytest.mark.asyncio
async def test_handoff_question(client: AsyncClient):
    """Happy-path: Handoff endpoint routes question to appropriate agent."""
    with patch("app.agents.search_agent.SearchAgent.process") as mock_search, \
         patch("app.agents.llm_agent.LLMAgent.process") as mock_llm, \
         patch("app.agents.orchestration.HandoffOrchestration._ai_route_question") as mock_route:
        
        # Mock AI routing to return SearchAgent
        mock_route.return_value = {
            "agent": "SearchAgent",
            "confidence": 0.9,
            "reasoning": "Question is about a film"
        }
        mock_search.return_value = "Alien (Horror) rents for $2.99."
        
        request_data = {"question": "What is the rental rate for Alien?"}
        response = await client.post("/api/v1/ai/handoff", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "SearchAgent"
        assert "answer" in data

