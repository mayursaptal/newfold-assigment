# Interview API

FastAPI application with SQLModel, Semantic Kernel (Gemini), Alembic migrations, and PostgreSQL in Docker.

## Quick Start

```bash
# 1. Copy environment file
cp .env.example .env
# Edit .env with your configuration (especially GEMINI_API_KEY)

# 2. Start services (Docker or Podman)
cd docker
docker-compose up -d
# Or: podman compose up -d

# 3. Database is automatically restored on first startup
# 4. Access API at http://localhost:8000
```

## Architecture

- **`app/`** - FastAPI entry-point
- **`api/v1/`** - API routes (films, rentals, customers, categories, AI)
- **`domain/`** - Business logic (models, repositories, services)
- **`core/`** - Infrastructure (settings, db, auth, logging, dependencies)
- **`migrations/`** - Alembic database migrations
- **`tests/`** - Test suite

## Database Restore

### Automatic Restoration (Recommended)

The Docker Compose setup automatically restores the Pagila database on first container creation. SQL files in `sql/` are mounted to PostgreSQL's initialization directory:

```bash
cd docker
docker-compose up -d
```

The database will be restored automatically from:
- `sql/01-pagila-schema.sql` (schema)
- `sql/02-pagila-data.sql` (data)

### Manual Restoration

**Option 1: Using Python script**
```bash
python scripts/restore_pagila.py
```

**Option 2: Using psql directly**
```bash
psql -h localhost -U postgres -d interview_db -f sql/01-pagila-schema.sql
psql -h localhost -U postgres -d interview_db -f sql/02-pagila-data.sql
```

**Option 3: Using container exec**
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

```bash
# Apply all pending migrations
alembic upgrade head
```

### Create New Migration

```bash
# Autogenerate migration from SQLModel changes
alembic revision --autogenerate -m "Description of changes"

# Manual migration
alembic revision -m "Description of changes"
```

### Migration Commands

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Upgrade to specific revision
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

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `GEMINI_API_KEY` - Google Gemini API key
- `SECRET_KEY` - JWT secret key
- `DEBUG` - Debug mode (True/False)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Development

### Run Locally

```bash
# Install dependencies
pip install -e ".[dev]"

# Run application
uvicorn app.main:app --reload
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_films.py
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
```

## Viewing Application Logs

The application uses structured logging with `structlog`. Logs are output to **stdout** and can be viewed through container logs.

### Container Logs (Recommended)

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

### Local Development

When running locally (not in container), logs appear directly in the terminal:

```bash
uvicorn app.main:app --reload
```

Logs will be printed to the console where you run the command.

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
interview/
├── app/                    # FastAPI entry-point
│   └── main.py
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
│   └── logging.py          # Logging
├── migrations/             # Alembic migrations
│   └── versions/
├── tests/                  # Test suite
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
- ✅ Google Gemini AI integration
- ✅ Alembic database migrations
- ✅ PostgreSQL in Docker/Podman
- ✅ Dependency injection throughout
- ✅ Structured logging with structlog
- ✅ Bearer token authentication
- ✅ Comprehensive test suite
- ✅ Pydoc documentation

## License

MIT
