"""AI API routes using Azure OpenAI.

This module defines FastAPI routes for AI-powered endpoints using Azure OpenAI.
It provides endpoints for chat completions and film summaries.

Endpoints:
    GET /api/v1/ai/ask?question=... - Ask a question and get streaming response
    POST /api/v1/ai/summary - Get AI-generated film summary with structured JSON

Example:
    ```python
    # Ask a question
    GET /api/v1/ai/ask?question=What is artificial intelligence?
    
    # Get film summary
    POST /api/v1/ai/summary
    {
        "film_id": 1
    }
    ```
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from domain.services import AIService, FilmService, HandoffService
from domain.schemas import FilmSummaryRequest, FilmSummaryResponse, HandoffRequest, HandoffResponse
from core.dependencies import get_ai_service, get_film_service, get_handoff_service

router = APIRouter()


@router.get("/ask")
async def ask_question(
    question: str = Query(..., description="Question to ask the AI"),
    service: AIService = Depends(get_ai_service),
):
    """
    Ask a question to the AI and get a streaming text response.
    
    Args:
        question: Question to ask
        service: AI service (injected)
        
    Returns:
        Streaming plain text response
    """
    async def generate_stream():
        async for chunk in service.stream_chat(question):
            yield chunk
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.post("/summary", response_model=FilmSummaryResponse)
async def get_film_summary(
    request: FilmSummaryRequest,
    ai_service: AIService = Depends(get_ai_service),
    film_service: FilmService = Depends(get_film_service),
):
    """
    Get AI-generated summary for a film with structured JSON response.
    
    Uses Semantic Kernel's invoke method with prompt template and JSON response format.
    
    Args:
        request: Film summary request with film_id
        ai_service: AI service (injected)
        film_service: Film service (injected) - used to look up film
        
    Returns:
        Structured JSON with title, rating, and recommended fields
    """
    summary = await ai_service.get_film_summary(request.film_id, film_service)
    return FilmSummaryResponse(**summary)


@router.post("/handoff", response_model=HandoffResponse)
async def handoff_question(
    request: HandoffRequest,
    service: HandoffService = Depends(get_handoff_service),
):
    """
    Route question to appropriate agent using handoff orchestration.
    
    Uses Semantic Kernel's HandoffOrchestration following Microsoft documentation pattern:
    - Creates orchestration with SearchAgent and LLMAgent
    - Uses OrchestrationHandoffs configuration for automatic routing
    - Handles handoffs based on agent responses and descriptions
    
    Args:
        request: Handoff request with question
        service: Handoff service (injected)
        
    Returns:
        Response with agent name and answer
    """
    result = await service.process_question(request.question)
    return HandoffResponse(agent=result["agent"], answer=result["answer"])
