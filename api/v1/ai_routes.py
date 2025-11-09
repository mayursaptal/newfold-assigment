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
from pydantic import BaseModel
from domain.services import AIService, FilmService
from domain.schemas import FilmSummaryRequest, FilmSummaryResponse
from core.dependencies import get_ai_service, get_film_service, get_db_session, get_ai_kernel
from app.agents import HandoffOrchestration, SearchAgent, LLMAgent
from domain.repositories import FilmRepository
from semantic_kernel import Kernel
from sqlalchemy.ext.asyncio import AsyncSession

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


@router.post("/handoff", response_model=HandoffResponse)
async def handoff_question(
    request: HandoffRequest,
    session: AsyncSession = Depends(get_db_session),
    kernel: Kernel = Depends(get_ai_kernel),
):
    """
    Route question to appropriate agent using handoff orchestration.
    
    Uses HandoffOrchestration to route questions:
    - Questions containing "film" keyword → SearchAgent (searches database)
    - Other questions → LLMAgent (uses Semantic Kernel)
    
    If SearchAgent finds no match, automatically hands off to LLMAgent.
    
    Args:
        request: Handoff request with question
        session: Database session (injected)
        kernel: Semantic Kernel instance (injected)
        
    Returns:
        Response with agent name and answer
    """
    # Create agents
    film_repository = FilmRepository(session)
    search_agent = SearchAgent(film_repository, kernel=kernel)
    llm_agent = LLMAgent(kernel)
    
    # Create orchestration with custom routing logic
    # Uses OrchestrationHandoffs for configuration but custom process() method
    orchestration = HandoffOrchestration(search_agent, llm_agent)
    
    # Process question using custom routing logic
    result = await orchestration.process(request.question)
    
    return HandoffResponse(**result)
