# System Patterns

## Architecture Pattern

### Layered Architecture with Dependency Injection

The project follows a **layered architecture** pattern inspired by pagila_api:

```
┌─────────────────────────────────────┐
│         app/ (Entry Point)          │
│      FastAPI initialization         │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│      api/v1/ (Presentation)         │
│      HTTP routes & validation       │
└─────────────────────────────────────┘
                  │
                  ▼ (Dependency Injection)
┌─────────────────────────────────────┐
│      domain/ (Business Logic)       │
│  ┌──────────┐  ┌──────────────┐   │
│  │ Services │  │ Repositories │   │
│  └──────────┘  └──────────────┘   │
│  ┌──────────────────────────────┐  │
│  │        Models (SQLModel)     │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│      core/ (Infrastructure)        │
│  Database │ Auth │ AI │ Logging    │
└─────────────────────────────────────┘
```

## Key Design Patterns

### 1. Dependency Injection

FastAPI's dependency injection system is used throughout:

- **Database Sessions**: Injected via `get_db_session()`
- **Repositories**: Injected via `get_*_repository()`
- **Services**: Injected via `get_*_service()`
- **AI Kernel**: Injected via `get_ai_kernel()`

**Location**: `core/dependencies.py`

**Example**:
```python
@router.get("/films")
async def get_films(
    service: FilmService = Depends(get_film_service)
):
    return await service.get_films()
```

### 2. Repository Pattern

Data access is abstracted through repositories:

- **FilmRepository**: Film data access
- **RentalRepository**: Rental data access

**Location**: `domain/repositories.py`

**Benefits**:
- Separation of concerns
- Easy to test (mock repositories)
- Database-agnostic business logic

### 3. Service Layer Pattern

Business logic is encapsulated in services:

- **FilmService**: Film business logic
- **RentalService**: Rental business logic
- **AIService**: AI operations

**Location**: `domain/services.py`

**Benefits**:
- Reusable business logic
- Testable without HTTP layer
- Framework-agnostic

### 4. Configuration Pattern

Two-tier configuration system:

1. **Environment Variables** (`.env`) - Runtime configuration
2. **TOML Files** (`config/config.toml`) - Default configuration

**Location**: `core/settings.py`, `core/config.py`

**Precedence**: Environment variables override TOML values

### 5. Factory Pattern

Infrastructure components use factory functions:

- **create_kernel()**: Semantic Kernel factory
- **get_async_session()**: Database session factory

**Location**: `core/ai_kernel.py`, `core/db.py`

## Component Relationships

### Request Flow

```
HTTP Request
    │
    ▼
api/v1/*_routes.py (Route Handler)
    │
    ▼ (Dependency Injection)
domain/services.py (Business Logic)
    │
    ▼ (Dependency Injection)
domain/repositories.py (Data Access)
    │
    ▼
core/db.py (Database Session)
    │
    ▼
PostgreSQL Database
```

### Dependency Graph

```
app/main.py
    ├── api/v1/router
    │   ├── film_routes → FilmService
    │   ├── rental_routes → RentalService
    │   └── ai_routes → AIService
    │
    └── core/
        ├── settings.py (used by all)
        ├── db.py (used by repositories)
        ├── dependencies.py (injection functions)
        ├── ai_kernel.py (used by AIService)
        ├── auth.py (optional, for protected routes)
        └── logging.py (used by all)
```

## Data Flow

### Create Film Example

1. **HTTP Request** → `POST /api/v1/films/`
2. **Route Handler** → `film_routes.create_film()`
3. **Dependency Injection** → `FilmService` injected
4. **Service** → `FilmService.create_film()`
5. **Dependency Injection** → `FilmRepository` injected
6. **Repository** → `FilmRepository.create()`
7. **Database** → SQLModel insert operation
8. **Response** → FilmRead model returned

## Testing Patterns

### Test Structure

- **conftest.py**: Shared fixtures (database session, test client)
- **test_*.py**: Feature-specific tests

### Test Database

- Uses in-memory SQLite for tests
- Each test gets a fresh database session
- Dependency overrides for test isolation

**Location**: `tests/conftest.py`

## Migration Pattern

### Alembic Workflow

1. **Model Changes** → Update `domain/models.py`
2. **Generate Migration** → `alembic revision --autogenerate`
3. **Review Migration** → Check generated SQL
4. **Apply Migration** → `alembic upgrade head`

**Location**: `migrations/env.py`

## Logging Pattern

### Structured Logging

- Uses `structlog` for JSON logging
- Context variables for request tracking
- Log level from environment

**Location**: `core/logging.py`

## Authentication Pattern

### Bearer Token

- JWT-based authentication
- Token validation via dependency
- Optional protection on routes

**Location**: `core/auth.py`

**Usage**:
```python
@router.get("/protected")
async def protected_route(
    current_user: dict = Depends(get_current_user)
):
    return {"user": current_user}
```

