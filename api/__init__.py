"""API layer package.

This package contains the API layer of the Interview API, implementing
RESTful HTTP endpoints using FastAPI. The API layer handles HTTP requests,
validation, and response formatting.

Structure:
    - v1/: API version 1 endpoints and routing

Key Features:
    - RESTful API design following HTTP standards
    - Automatic request/response validation via Pydantic
    - OpenAPI documentation generation
    - Dependency injection for services and repositories
    - Proper HTTP status codes and error handling
    - Authentication support where required

Endpoints:
    - /api/v1/films/: Film CRUD operations
    - /api/v1/rentals/: Rental CRUD operations
    - /api/v1/categories/: Category read operations
    - /api/v1/customers/: Customer rental operations
    - /api/v1/ai/: AI-powered endpoints (chat, summaries, handoff)

Example:
    ```python
    from fastapi import APIRouter, Depends
    from domain.services import FilmService

    router = APIRouter()

    @router.get("/films/")
    async def get_films(service: FilmService = Depends(get_film_service)):
        return await service.get_films()
    ```
"""
