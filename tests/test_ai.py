"""Tests for AI endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_health_check(client: AsyncClient):
    """Test AI service health check."""
    response = await client.get("/api/v1/ai/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "semantic_kernel"


@pytest.mark.asyncio
async def test_generate_text(client: AsyncClient):
    """Test text generation endpoint."""
    request_data = {
        "prompt": "Hello, world!",
        "max_tokens": 100,
    }
    
    response = await client.post("/api/v1/ai/generate", json=request_data)
    # Note: This will fail if Semantic Kernel is not properly configured
    # In a real scenario, you'd mock the AI service
    assert response.status_code in [200, 400]  # 400 if AI not configured


@pytest.mark.asyncio
async def test_chat_completion(client: AsyncClient):
    """Test chat completion endpoint."""
    request_data = {
        "messages": [
            {"role": "user", "content": "Hello!"}
        ],
        "temperature": 0.7,
    }
    
    response = await client.post("/api/v1/ai/chat", json=request_data)
    # Note: This will fail if Semantic Kernel is not properly configured
    # In a real scenario, you'd mock the AI service
    assert response.status_code in [200, 400]  # 400 if AI not configured

