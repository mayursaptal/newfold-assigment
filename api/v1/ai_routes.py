"""AI API routes using Gemini.

This module defines FastAPI routes for AI-powered endpoints using Google's
Gemini API. It provides endpoints for chat completions and film summaries.

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
from domain.services import AIService, FilmService
from domain.schemas import FilmSummaryRequest, FilmSummaryResponse
from core.dependencies import get_ai_service, get_film_service

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
