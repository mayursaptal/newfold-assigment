"""Domain layer package.

This package contains the domain layer of the Interview API, implementing
the business logic and data models following Domain-Driven Design principles.

The domain layer is organized into:
    - models/: SQLModel entities representing database tables
    - repositories/: Data access layer implementing repository pattern
    - services/: Business logic layer orchestrating operations
    - schemas/: Pydantic schemas for API request/response validation

Architecture:
    API Layer → Services → Repositories → Database

Key Features:
    - Type-safe models using SQLModel
    - Repository pattern for data access abstraction
    - Service layer for business logic encapsulation
    - Pydantic schemas for API validation
    - Async/await throughout for performance

Example:
    ```python
    from domain.services import FilmService
    from domain.repositories import FilmRepository
    from domain.schemas import FilmCreate

    # Service orchestrates business logic
    service = FilmService(repository)
    film = await service.create_film(FilmCreate(...))
    ```
"""
