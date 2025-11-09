"""AI/Semantic Kernel API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from domain.services import AIService
from core.dependencies import get_ai_service

router = APIRouter()


class TextGenerationRequest(BaseModel):
    """Text generation request model."""
    prompt: str
    max_tokens: int = 2000


class TextGenerationResponse(BaseModel):
    """Text generation response model."""
    text: str


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    """Chat completion request model."""
    messages: List[ChatMessage]
    temperature: float = 0.7


class ChatCompletionResponse(BaseModel):
    """Chat completion response model."""
    response: str


@router.post("/generate", response_model=TextGenerationResponse)
async def generate_text(
    request: TextGenerationRequest,
    service: AIService = Depends(get_ai_service),
):
    """
    Generate text using Semantic Kernel.
    
    Args:
        request: Text generation request
        service: AI service (injected)
        
    Returns:
        Generated text
    """
    try:
        text = await service.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
        )
        return TextGenerationResponse(text=text)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/chat", response_model=ChatCompletionResponse)
async def chat_completion(
    request: ChatCompletionRequest,
    service: AIService = Depends(get_ai_service),
):
    """
    Chat completion using Semantic Kernel.
    
    Args:
        request: Chat completion request
        service: AI service (injected)
        
    Returns:
        Chat response
    """
    try:
        messages = [msg.model_dump() for msg in request.messages]
        response = await service.chat_completion(
            messages=messages,
            temperature=request.temperature,
        )
        return ChatCompletionResponse(response=response)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/health")
async def ai_health_check(
    service: AIService = Depends(get_ai_service),
):
    """
    Health check for AI service.
    
    Args:
        service: AI service (injected)
        
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "semantic_kernel",
    }

