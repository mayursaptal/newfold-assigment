"""FastAPI application main entry point.

This module creates and configures the FastAPI application instance,
sets up middleware, registers routes, and handles application lifecycle
events (startup and shutdown).

The application uses:
    - FastAPI for the web framework
    - SQLModel for database ORM
    - Semantic Kernel for AI operations
    - PostgreSQL for the database
    - Structured JSON logging

Example:
    Run the application:
    ```bash
    uvicorn app.main:app --reload
    ```
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.settings import settings
from core.logging import setup_logging, get_logger
from core.db import init_db, close_db
from api.v1 import router as v1_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting application", debug=settings.debug)
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Interview API",
    description="FastAPI application with SQLModel, Semantic Kernel, and PostgreSQL",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(v1_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint.
    
    Returns basic API information and links to documentation.
    
    Returns:
        dict: API information including message, version, and docs URL
    """
    return {
        "message": "Interview API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint.
    
    Used for monitoring and load balancer health checks.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "interview-api",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

