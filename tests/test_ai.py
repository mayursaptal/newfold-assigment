"""Tests for AI endpoints - one happy-path test per endpoint.

This module contains pytest tests for all AI-related API endpoints.
Each endpoint has exactly one happy-path test that verifies successful
operation. AI service methods are mocked to avoid actual API calls.

Test Coverage:
    - GET /api/v1/ai/ask?question=... - Ask question (streaming)
    - POST /api/v1/ai/summary - Get film summary (structured JSON)

Note:
    AI service methods are mocked to avoid external API calls during testing.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_ask_question(client: AsyncClient):
    """Happy-path: Ask a question to the AI and get streaming response."""
    # Mock the AI service to avoid actual API calls
    with patch("domain.services.ai_service.AIService.stream_chat") as mock_stream:
        # Mock streaming response
        async def mock_stream_generator():
            yield "Hello"
            yield " "
            yield "World"
        
        mock_stream.return_value = mock_stream_generator()
        
        response = await client.get("/api/v1/ai/ask?question=hello")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        # For streaming, we check the status code and content type
        # The actual content would be streamed


@pytest.mark.asyncio
async def test_get_film_summary(client: AsyncClient):
    """Happy-path: Get AI-generated summary for a film."""
    # Mock the AI service to avoid actual API calls
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
        assert "title" in data
        assert "rating" in data
        assert "recommended" in data
        assert isinstance(data["recommended"], bool)
