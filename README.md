# Interview API

FastAPI application with SQLModel, Semantic Kernel, TOML configuration, Alembic migrations, and PostgreSQL in Docker.

## Architecture

This project follows a **layered architecture with dependency injection** pattern, inspired by the pagila_api structure:

- **`app/`** - FastAPI entry-point only (thin layer)
- **`api/v1/`** - API presentation layer (routes)
- **`domain/`** - Pure business rules, no FastAPI dependencies
  - `models.py` - SQLModel entities
  - `repositories.py` - DB access layer (repository pattern)
  - `services.py` - Use-cases (business logic, AI adapter)
- **`core/`** - Reusable, infra-agnostic helpers (shared library)
  - `settings.py` - Pydantic BaseSettings for .env
  - `config.py` - TOML file loader
  - `db.py` - Async engine + session factory
  - `dependencies.py` - FastAPI dependency injection
  - `ai_kernel.py` - Semantic Kernel factory
  - `auth.py` - Bearer-token guard
  - `logging.py` - structlog JSON setup

## Features

- ✅ FastAPI with async support
- ✅ SQLModel for type-safe ORM
- ✅ Semantic Kernel integration
- ✅ TOML configuration with environment variable override
- ✅ Alembic database migrations
- ✅ PostgreSQL in Docker
- ✅ Dependency injection throughout
- ✅ Structured logging with structlog
- ✅ Bearer token authentication
- ✅ Comprehensive test suite

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- PostgreSQL (via Docker)

## Setup

### 1. Clone and Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- Database credentials
- Semantic Kernel API key
- Secret key for JWT

### 3. Start PostgreSQL

```bash
cd docker
docker-compose up -d
```

This will start PostgreSQL on port 5432.

### 4. Run Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload

# Or use the main module
python -m app.main
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
interview/
├── app/                    # FastAPI entry-point only
│   └── main.py
├── api/                    # API presentation layer
│   └── v1/
│       ├── film_routes.py
│       ├── rental_routes.py
│       └── ai_routes.py
├── domain/                 # Pure business rules
│   ├── models.py          # SQLModel entities
│   ├── repositories.py    # DB access layer
│   └── services.py        # Use-cases
├── core/                   # Shared infrastructure
│   ├── settings.py        # Pydantic BaseSettings
│   ├── config.py          # TOML loader
│   ├── db.py              # Database setup
│   ├── dependencies.py    # Dependency injection
│   ├── ai_kernel.py       # Semantic Kernel
│   ├── auth.py            # Authentication
│   └── logging.py         # Logging setup
├── migrations/             # Alembic migrations
├── tests/                  # Test suite
├── docker/                 # Docker configuration
│   └── docker-compose.yml
├── config/                 # Configuration files
│   └── config.toml
├── pyproject.toml          # Project configuration
└── alembic.ini            # Alembic configuration
```

## API Endpoints

### Films
- `GET /api/v1/films/` - List all films
- `GET /api/v1/films/{id}` - Get film by ID
- `POST /api/v1/films/` - Create film
- `PUT /api/v1/films/{id}` - Update film
- `DELETE /api/v1/films/{id}` - Delete film

### Rentals
- `GET /api/v1/rentals/` - List all rentals
- `GET /api/v1/rentals/{id}` - Get rental by ID
- `POST /api/v1/rentals/` - Create rental
- `PUT /api/v1/rentals/{id}` - Update rental
- `DELETE /api/v1/rentals/{id}` - Delete rental

### AI
- `POST /api/v1/ai/generate` - Generate text
- `POST /api/v1/ai/chat` - Chat completion
- `GET /api/v1/ai/health` - Health check

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_films.py
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current
```

## Development

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .
```

## Configuration

### Environment Variables (.env)

- `DATABASE_URL` - PostgreSQL connection string
- `POSTGRES_*` - Database configuration
- `SEMANTIC_KERNEL_API_KEY` - AI service API key
- `SEMANTIC_KERNEL_ENDPOINT` - AI service endpoint
- `SECRET_KEY` - JWT secret key
- `DEBUG` - Debug mode
- `LOG_LEVEL` - Logging level

### TOML Configuration (config/config.toml)

Application settings can be defined in `config/config.toml`. Environment variables take precedence over TOML values.

## Dependency Injection

The project uses FastAPI's dependency injection system throughout:

- Database sessions are injected via `get_db_session()`
- Repositories are injected via `get_*_repository()`
- Services are injected via `get_*_service()`
- AI Kernel is injected via `get_ai_kernel()`

Example:
```python
@router.get("/films")
async def get_films(
    service: FilmService = Depends(get_film_service)
):
    return await service.get_films()
```

## License

MIT

