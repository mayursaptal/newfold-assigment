# Interview API

FastAPI application with SQLModel, Semantic Kernel (OpenAI), Alembic migrations, and PostgreSQL.

## Quick Start

### Using Docker/Podman (Recommended)

```bash
# 1. Copy environment file
cp .env.example .env
# Edit .env with your configuration (especially OPENAI_API_KEY)

# 2. Start services
cd docker
docker-compose up -d
# Or: podman compose up -d

# 3. Database is automatically restored on first startup
# 4. Access API at http://localhost:8000
```

### Running Locally (Without Docker)

```bash
# 1. Install PostgreSQL locally or use Docker for database only
# 2. Copy environment file
cp .env.example .env
# Edit .env with your configuration

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -e ".[dev]"

# 5. Set up database (see Database Restore section)
# 6. Run migrations
alembic upgrade head

# 7. Run application
uvicorn app.main:app --reload
```

## Running the Application

### Option 1: Using Docker/Podman (Recommended)

**Start all services:**
```bash
cd docker
docker-compose up -d
# Or: podman compose up -d
```

**View logs:**
```bash
# All services
docker-compose logs -f
# Or: podman compose logs -f

# FastAPI only
docker-compose logs -f fastapi
# Or: podman compose logs -f fastapi
```

**Stop services:**
```bash
docker-compose down
# Or: podman compose down
```

**Restart services:**
```bash
docker-compose restart
# Or: podman compose restart
```

**Rebuild containers:**
```bash
docker-compose up -d --build
# Or: podman compose up -d --build
```

**Run commands inside container:**
```bash
# Docker
docker exec -it interview_fastapi bash

# Podman
podman exec -it interview_fastapi bash
```

### Option 2: Running Locally (Without Docker)

**Prerequisites:**
- Python 3.10+
- PostgreSQL 15+ (running locally or in Docker)
- Virtual environment (recommended)

**Steps:**

1. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -e ".[dev]"
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your database and OpenAI configuration
```

4. **Set up database:**
   - Ensure PostgreSQL is running
   - Create database: `createdb interview_db`
   - Restore Pagila database (see Database Restore section)

5. **Run migrations:**
```bash
alembic upgrade head
```

6. **Start application:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access API:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests

### Option 1: Running Tests in Docker/Podman

**Run all tests:**
```bash
# Docker
docker exec interview_fastapi python3 -m pytest /app/tests/ -v

# Podman
podman exec interview_fastapi python3 -m pytest /app/tests/ -v

# Or using compose
cd docker
docker-compose exec fastapi python3 -m pytest /app/tests/ -v
podman compose exec fastapi python3 -m pytest /app/tests/ -v
```

**Run specific test file:**
```bash
docker exec interview_fastapi python3 -m pytest /app/tests/test_films.py -v
podman exec interview_fastapi python3 -m pytest /app/tests/test_films.py -v
```

**Run specific test:**
```bash
docker exec interview_fastapi python3 -m pytest /app/tests/test_films.py::test_create_film -v
podman exec interview_fastapi python3 -m pytest /app/tests/test_films.py::test_create_film -v
```

**Run with coverage:**
```bash
docker exec interview_fastapi python3 -m pytest /app/tests/ --cov=. --cov-report=html -v
podman exec interview_fastapi python3 -m pytest /app/tests/ --cov=. --cov-report=html -v
```

**Run with verbose output:**
```bash
docker exec interview_fastapi python3 -m pytest /app/tests/ -v --tb=short
podman exec interview_fastapi python3 -m pytest /app/tests/ -v --tb=short
```

### Option 2: Running Tests Locally (Without Docker)

**Prerequisites:**
- All dependencies installed (including dev dependencies)
- Virtual environment activated
- Test database configured (uses in-memory SQLite by default)

**Steps:**

1. **Ensure dependencies are installed:**
```bash
pip install -e ".[dev]"
```

2. **Run all tests:**
```bash
pytest tests/ -v
```

3. **Run specific test file:**
```bash
pytest tests/test_films.py -v
```

4. **Run specific test:**
```bash
pytest tests/test_films.py::test_create_film -v
```

5. **Run with coverage:**
```bash
pytest tests/ --cov=. --cov-report=html -v
```

6. **Run with verbose output:**
```bash
pytest tests/ -v --tb=short
```

**Test Configuration:**
- Tests use in-memory SQLite database (configured in `tests/conftest.py`)
- No external dependencies required for tests
- AI endpoints are mocked to avoid actual API calls

## Database Restore

### Automatic Restoration (Recommended - Docker/Podman)

The Docker Compose setup automatically restores the Pagila database on first container creation. SQL files in `sql/` are mounted to PostgreSQL's initialization directory:

```bash
cd docker
docker-compose up -d
```

The database will be restored automatically from:
- `sql/01-pagila-schema.sql` (schema)
- `sql/02-pagila-data.sql` (data)

### Manual Restoration

**Option 1: Using Python script (Local)**
```bash
python scripts/restore_pagila.py
```

**Option 2: Using psql directly (Local)**
```bash
psql -h localhost -U postgres -d interview_db -f sql/01-pagila-schema.sql
psql -h localhost -U postgres -d interview_db -f sql/02-pagila-data.sql
```

**Option 3: Using container exec (Docker/Podman)**
```bash
# Docker
docker exec -i interview_postgres psql -U postgres -d interview_db < sql/01-pagila-schema.sql
docker exec -i interview_postgres psql -U postgres -d interview_db < sql/02-pagila-data.sql

# Podman
podman exec -i interview_postgres psql -U postgres -d interview_db < sql/01-pagila-schema.sql
podman exec -i interview_postgres psql -U postgres -d interview_db < sql/02-pagila-data.sql
```

## Database Migrations

Alembic is configured for database schema management.

### Apply Migrations

**In Docker/Podman:**
```bash
# Docker
docker exec interview_fastapi alembic upgrade head

# Podman
podman exec interview_fastapi alembic upgrade head

# Or using compose
cd docker
docker-compose exec fastapi alembic upgrade head
podman compose exec fastapi alembic upgrade head
```

**Locally:**
```bash
# Apply all pending migrations
alembic upgrade head
```

### Create New Migration

**In Docker/Podman:**
```bash
# Docker
docker exec interview_fastapi alembic revision --autogenerate -m "Description of changes"

# Podman
podman exec interview_fastapi alembic revision --autogenerate -m "Description of changes"
```

**Locally:**
```bash
# Autogenerate migration from SQLModel changes
alembic revision --autogenerate -m "Description of changes"

# Manual migration
alembic revision -m "Description of changes"
```

### Migration Commands

**Show current revision:**
```bash
# Docker/Podman
docker exec interview_fastapi alembic current
podman exec interview_fastapi alembic current

# Local
alembic current
```

**Show migration history:**
```bash
# Docker/Podman
docker exec interview_fastapi alembic history
podman exec interview_fastapi alembic history

# Local
alembic history
```

**Rollback one migration:**
```bash
# Docker/Podman
docker exec interview_fastapi alembic downgrade -1
podman exec interview_fastapi alembic downgrade -1

# Local
alembic downgrade -1
```

**Rollback to specific revision:**
```bash
# Docker/Podman
docker exec interview_fastapi alembic downgrade <revision_id>
podman exec interview_fastapi alembic downgrade <revision_id>

# Local
alembic downgrade <revision_id>
```

**Upgrade to specific revision:**
```bash
# Docker/Podman
docker exec interview_fastapi alembic upgrade <revision_id>
podman exec interview_fastapi alembic upgrade <revision_id>

# Local
alembic upgrade <revision_id>
```

### Included Migrations

- **001_add_streaming_available_to_film**: Adds `streaming_available` Boolean column (DEFAULT FALSE) to `film` table
- **002_create_streaming_subscription_table**: Creates `streaming_subscription` table with id, customer_id FK, plan_name, start_date, end_date

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Films

**Get all films (paginated)**
```bash
curl -X GET "http://localhost:8000/api/v1/films/?skip=0&limit=10"
```

**Get films by category**
```bash
curl -X GET "http://localhost:8000/api/v1/films/?category=Action&skip=0&limit=10"
```

**Get film by ID**
```bash
curl -X GET "http://localhost:8000/api/v1/films/1"
```

**Create film**
```bash
curl -X POST "http://localhost:8000/api/v1/films/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Matrix",
    "description": "A computer hacker learns about the true nature of reality",
    "release_year": 1999,
    "language_id": 1,
    "rental_duration": 3,
    "rental_rate": 4.99,
    "length": 136,
    "replacement_cost": 19.99,
    "rating": "R"
  }'
```

**Update film**
```bash
curl -X PUT "http://localhost:8000/api/v1/films/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Matrix Reloaded",
    "rental_rate": 5.99
  }'
```

**Delete film**
```bash
curl -X DELETE "http://localhost:8000/api/v1/films/1"
```

### Rentals

**Get all rentals (paginated)**
```bash
curl -X GET "http://localhost:8000/api/v1/rentals/?skip=0&limit=10"
```

**Get rental by ID**
```bash
curl -X GET "http://localhost:8000/api/v1/rentals/1"
```

**Create rental**
```bash
curl -X POST "http://localhost:8000/api/v1/rentals/" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_id": 1,
    "customer_id": 1,
    "staff_id": 1
  }'
```

**Update rental (return date)**
```bash
curl -X PUT "http://localhost:8000/api/v1/rentals/1" \
  -H "Content-Type: application/json" \
  -d '{
    "return_date": "2024-11-10T10:00:00Z"
  }'
```

**Delete rental**
```bash
curl -X DELETE "http://localhost:8000/api/v1/rentals/1"
```

### Customers

**Get customer rentals**
```bash
curl -X GET "http://localhost:8000/api/v1/customers/1/rentals?skip=0&limit=10"
```

**Create customer rental (requires Bearer token with 'dvd_' prefix)**
```bash
curl -X POST "http://localhost:8000/api/v1/customers/1/rentals" \
  -H "Authorization: Bearer dvd_admin" \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_id": 1,
    "staff_id": 1
  }'
```

### Categories

**Get all categories (paginated)**
```bash
curl -X GET "http://localhost:8000/api/v1/categories?skip=0&limit=10"
```

**Get category by ID**
```bash
curl -X GET "http://localhost:8000/api/v1/categories/1"
```

### AI Endpoints

**Ask question (streaming response)**
```bash
curl -X GET "http://localhost:8000/api/v1/ai/ask?question=What%20is%20artificial%20intelligence?"
```

**Get film summary (structured JSON)**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "film_id": 1
  }'
```

**Handoff orchestration (agent routing)**
```bash
# SearchAgent chosen (film question)
curl -X POST "http://localhost:8000/api/v1/ai/handoff" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the rental rate for the film Alien?"
  }'

# Response:
# {
#   "agent": "SearchAgent",
#   "answer": "Alien (Horror) rents for $2.99."
# }

# LLMAgent chosen (general question)
curl -X POST "http://localhost:8000/api/v1/ai/handoff" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who won the FIFA World Cup in 2022?"
  }'

# Response:
# {
#   "agent": "LLMAgent",
#   "answer": "Argentina won the 2022 FIFA World Cup after defeating France."
# }
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Environment Variables

The following environment variables can be set in a `.env` file or as system environment variables:

- `DATABASE_URL` - PostgreSQL connection URL
- `POSTGRES_*` - Individual PostgreSQL connection parameters
- `DEBUG` - Debug mode (True/False)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `SECRET_KEY` - Secret key for JWT token signing
- `API_V1_PREFIX` - API version 1 URL prefix
- `OPENAI_API_KEY` - OpenAI API key (required for AI features)
- `OPENAI_MODEL` - OpenAI model name to use (default: gpt-4)
- `OPENAI_ORG_ID` - OpenAI organization ID (optional)
- `HOST` - Server host address
- `PORT` - Server port number

### Secret Management

**⚠️ IMPORTANT: Security Best Practices**

- `.env.example` contains **placeholder values only** - never commit actual secrets
- In production, inject secrets via:
  - Docker environment variables: `docker run -e SECRET_KEY=...`
  - Kubernetes secrets
  - CI/CD secret management (GitHub Secrets, GitLab CI variables, etc.)
  - Cloud provider secret managers (AWS Secrets Manager, Azure Key Vault, etc.)

**Local Development:**
1. Copy `.env.example` to `.env`
2. Replace placeholder values with your actual secrets
3. Ensure `.env` is in `.gitignore` (already configured)

**Production:**
- Never use `.env` files in production
- Always inject secrets via environment variables or secret management systems

## Development

### Setup

**Local Development:**
```bash
# Install dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks (recommended)
pre-commit install

# Run application
uvicorn app.main:app --reload
```

**Docker Development:**
```bash
cd docker
docker-compose up -d
# Application runs with auto-reload enabled
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. Hooks run automatically on commit and check:
- Code formatting (black)
- Linting (ruff)
- Type checking (mypy)

**Install hooks:**
```bash
pre-commit install
```

**Run hooks manually:**
```bash
pre-commit run --all-files
```

**Skip hooks (not recommended):**
```bash
git commit --no-verify
```

### Type Checking

Type checking is enforced via mypy. CI will fail on type errors.

**Run type checking locally:**
```bash
mypy . --config-file mypy.ini
```

**Run type checking in Docker:**
```bash
docker exec interview_fastapi mypy . --config-file mypy.ini
podman exec interview_fastapi mypy . --config-file mypy.ini
```

### Code Quality

**Format code:**
```bash
# Local
black .

# Docker/Podman
docker exec interview_fastapi black /app
podman exec interview_fastapi black /app
```

**Lint code:**
```bash
# Local
ruff check .
ruff check . --fix  # Auto-fix issues

# Docker/Podman
docker exec interview_fastapi ruff check /app
docker exec interview_fastapi ruff check /app --fix
podman exec interview_fastapi ruff check /app
podman exec interview_fastapi ruff check /app --fix
```

**Type check:**
```bash
# Local
mypy . --config-file mypy.ini

# Docker/Podman
docker exec interview_fastapi mypy /app --config-file mypy.ini
podman exec interview_fastapi mypy /app --config-file mypy.ini
```

### Container Management

```bash
cd docker

# Start services
docker-compose up -d
# Or: podman compose up -d

# View logs
docker-compose logs -f
# Or: podman compose logs -f

# Stop services
docker-compose down
# Or: podman compose down

# Rebuild containers
docker-compose up -d --build
# Or: podman compose up -d --build
```

## Viewing Application Logs

The application uses structured logging with `structlog`. Logs are output to **stdout** and can be viewed through container logs.

### Container Logs (Docker/Podman)

**View all service logs:**
```bash
cd docker
docker-compose logs -f
# Or: podman compose logs -f
```

**View FastAPI application logs only:**
```bash
# Docker
docker logs -f interview_fastapi

# Podman
podman logs -f interview_fastapi

# Or using compose
cd docker
docker-compose logs -f fastapi
podman compose logs -f fastapi
```

**View last N lines:**
```bash
docker logs --tail 100 interview_fastapi
podman logs --tail 100 interview_fastapi
```

**View logs with timestamps:**
```bash
docker logs -f -t interview_fastapi
podman logs -f -t interview_fastapi
```

### Local Development

When running locally (not in container), logs appear directly in the terminal:

```bash
uvicorn app.main:app --reload
```

Logs will be printed to the console where you run the command.

### Log Format

The log format depends on the `LOG_LEVEL` environment variable:

- **LOG_LEVEL=DEBUG**: Human-readable console format (colorized, easy to read)
- **LOG_LEVEL=INFO/WARNING/ERROR**: JSON format (structured, machine-readable)

Example JSON log:
```json
{"event": "Starting application", "debug": true, "timestamp": "2024-11-09T09:00:00Z", "logger": "app.main", "level": "info"}
```

Example DEBUG log:
```
2024-11-09 09:00:00 [info     ] Starting application    debug=True logger=app.main
```

### Log Levels

Set `LOG_LEVEL` in `.env` to control verbosity:
- `DEBUG` - Most verbose (includes SQL queries, detailed info)
- `INFO` - Standard information (default)
- `WARNING` - Warnings and errors only
- `ERROR` - Errors only
- `CRITICAL` - Critical errors only

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
interview/
├── app/                    # FastAPI entry-point
│   ├── main.py
│   └── agents/            # AI agents (SearchAgent, LLMAgent, Orchestration)
├── api/                    # API routes
│   └── v1/
│       ├── film_routes.py
│       ├── rental_routes.py
│       ├── customer_routes.py
│       ├── category_routes.py
│       └── ai_routes.py
├── domain/                 # Business logic
│   ├── models/            # SQLModel entities
│   ├── schemas/           # Pydantic schemas
│   ├── repositories/      # Data access layer
│   └── services/          # Business logic
├── core/                   # Infrastructure
│   ├── settings.py        # Configuration
│   ├── db.py              # Database setup
│   ├── dependencies.py    # Dependency injection
│   ├── auth.py            # Authentication
│   ├── ai_kernel.py       # AI kernel setup
│   ├── plugin_loader.py   # Semantic Kernel plugin loader
│   └── logging.py         # Logging
├── plugins/                # Semantic Kernel plugins
│   ├── chat/
│   ├── film_summary/
│   ├── film_short_summary/
│   ├── llm_agent/
│   └── orchestration/
├── migrations/             # Alembic migrations
│   └── versions/
├── tests/                  # Test suite
│   ├── conftest.py        # Test fixtures
│   ├── test_films.py
│   ├── test_rentals.py
│   ├── test_customers.py
│   ├── test_categories.py
│   └── test_ai.py
├── docker/                 # Container config
│   ├── docker-compose.yml
│   └── Dockerfile
├── sql/                    # Database SQL files
│   ├── 01-pagila-schema.sql
│   └── 02-pagila-data.sql
├── .env.example            # Environment template
└── pyproject.toml          # Project config
```

## Features

- ✅ FastAPI with async support
- ✅ SQLModel for type-safe ORM
- ✅ OpenAI (ChatGPT) AI integration via Semantic Kernel
- ✅ Alembic database migrations
- ✅ PostgreSQL in Docker/Podman
- ✅ Dependency injection throughout
- ✅ Structured logging with structlog
- ✅ Bearer token authentication
- ✅ Comprehensive test suite (17 happy-path tests)
- ✅ Pydoc documentation
- ✅ Semantic Kernel plugin system
- ✅ Agent orchestration (SearchAgent, LLMAgent)

## License

MIT
