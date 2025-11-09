# Interview API

FastAPI application with SQLModel, Semantic Kernel, Alembic migrations, and PostgreSQL in Docker.

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
  - `db.py` - Async engine + session factory
  - `dependencies.py` - FastAPI dependency injection
  - `ai_kernel.py` - Semantic Kernel factory
  - `auth.py` - Bearer-token guard
  - `logging.py` - structlog JSON setup

## Features

- ✅ FastAPI with async support
- ✅ SQLModel for type-safe ORM
- ✅ Semantic Kernel integration
- ✅ Alembic database migrations
- ✅ PostgreSQL in Docker
- ✅ Dependency injection throughout
- ✅ Structured logging with structlog
- ✅ Bearer token authentication
- ✅ Comprehensive test suite

## Prerequisites

- Python 3.10+
- **Container Runtime**: Docker or Podman (docker-compose works with both)
- PostgreSQL (via container)

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

### 3. Start Services and Restore Pagila Database

The Docker Compose setup works with both Docker and Podman. It will automatically restore the Pagila database and start FastAPI on first startup:

```bash
cd docker
docker-compose up -d
```

**Or with Podman:**
```bash
cd docker
podman compose up -d
```

This will:
- Start PostgreSQL container with automatic Pagila restoration from `sql/` folder
- Build and start FastAPI container
- Connect both containers on the same network

The SQL files in `sql/` will be automatically executed when the PostgreSQL container is created for the first time.

**View logs:**
```bash
cd docker
docker-compose logs -f
# Or with Podman:
podman compose logs -f
```

**Stop services:**
```bash
cd docker
docker-compose down
# Or with Podman:
podman compose down
```

**Rebuild containers:**
```bash
cd docker
docker-compose up -d --build
```

**Option B: Manual Restoration (If Needed)**

If you need to restore the database manually:

**Using Python script:**
```bash
python scripts/restore_pagila.py
```

**Using Shell script:**
```bash
./scripts/restore_pagila.sh
```

**Using psql directly:**
```bash
psql -h localhost -U postgres -d interview_db -f sql/pagila-schema.sql
psql -h localhost -U postgres -d interview_db -f sql/pagila-data.sql
```

This will start PostgreSQL on port 5432 and restore the Pagila sample database.

### 4. Run Migrations (Optional)

If you want to use Alembic migrations instead of the Pagila SQL files:

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Run the Application

**If using containers (Docker/Podman):**
The FastAPI application is already running in the container. Access it at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**If running locally (without containers):**

```bash
# Development mode
uvicorn app.main:app --reload

# Or use the main module
python -m app.main
```

### 6. Access the Application

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Container Management:**

- **View logs**: `cd docker && docker-compose logs -f`
- **View specific service**: `cd docker && docker-compose logs -f fastapi`
- **Restart services**: `cd docker && docker-compose restart`
- **Rebuild**: `cd docker && docker-compose up -d --build`

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
│   ├── db.py              # Database setup
│   ├── dependencies.py    # Dependency injection
│   ├── ai_kernel.py       # Semantic Kernel
│   ├── auth.py            # Authentication
│   └── logging.py         # Logging setup
├── migrations/             # Alembic migrations
├── tests/                  # Test suite
├── docker/                 # Container configuration (Docker/Podman)
│   ├── docker-compose.yml  # Works with both Docker and Podman
│   └── Dockerfile          # FastAPI container image
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

## Database Setup

### Restore Pagila Database

The project includes the Pagila sample database (a PostgreSQL sample database for learning and testing).

**Automatic Restoration:**
The Docker setup automatically restores Pagila on first container creation. The SQL files in `sql/` are mounted to the PostgreSQL container's initialization directory.

**Manual Restoration:**

**Recommended: Using Shell script (most reliable for large SQL files):**
```bash
./scripts/restore_pagila.sh
```

**Alternative methods:**

1. **Using Python script:**
   ```bash
   python scripts/restore_pagila.py
   ```
   Note: For very large SQL files, the shell script is more reliable.

2. **Using psql directly:**
   ```bash
   psql -h localhost -U postgres -d interview_db -f sql/01-pagila-schema.sql
   psql -h localhost -U postgres -d interview_db -f sql/02-pagila-data.sql
   ```

3. **Using container exec (if container is running):**
   ```bash
   # With Docker
   docker exec -i interview_postgres psql -U postgres -d interview_db < sql/01-pagila-schema.sql
   docker exec -i interview_postgres psql -U postgres -d interview_db < sql/02-pagila-data.sql
   
   # Or with Podman
   podman exec -i interview_postgres psql -U postgres -d interview_db < sql/01-pagila-schema.sql
   podman exec -i interview_postgres psql -U postgres -d interview_db < sql/02-pagila-data.sql
   ```

### Database Migrations (Alembic)

Alembic is configured to compare SQLModel metadata with the database schema using autogenerate.

**Example Migrations Included:**
- **Migration #1**: Adds Boolean column `streaming_available` (DEFAULT FALSE) to `film` table
- **Migration #2**: Creates `streaming_subscription` table (id, customer_id FK, plan_name, start_date, end_date) using Alembic's `op.create_table()` helper

**Create a new migration (autogenerate):**
```bash
# Compare SQLModel metadata with DB schema and generate migration
alembic revision --autogenerate -m "Description"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback one migration:**
```bash
alembic downgrade -1
```

**Show current revision:**
```bash
alembic current
```

**Autogenerate Configuration:**
The `migrations/env.py` is configured with:
- `compare_type=True` - Compares column types
- `compare_server_default=True` - Compares server defaults

This allows Alembic to detect differences between your SQLModel models and the actual database schema.

**Note:** If you're using the Pagila database, you may want to skip Alembic migrations or use them only for custom schema changes beyond Pagila.

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

