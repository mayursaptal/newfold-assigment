"""Application layer package.

This package contains the application layer of the Interview API,
including the main FastAPI application and AI agent orchestration.

Structure:
    - main.py: FastAPI application entry point and configuration
    - agents/: AI agent implementations using Semantic Kernel

Key Features:
    - FastAPI application setup and configuration
    - CORS middleware for cross-origin requests
    - Application lifecycle management (startup/shutdown)
    - AI agent orchestration using Semantic Kernel
    - Structured logging throughout

AI Agents:
    - SearchAgent: Handles film-related questions using database queries
    - LLMAgent: Handles general questions using LLM capabilities
    - HandoffOrchestration: Routes questions between agents intelligently

Example:
    ```python
    from app.main import app
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)
    ```
"""