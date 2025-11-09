# Technical Context

## Technology Stack

### Core Framework
- **FastAPI** (0.104.1+) - Modern async web framework
- **Uvicorn** - ASGI server
- **Python** 3.10+ - Programming language

### Database
- **SQLModel** (0.0.14+) - Type-safe ORM built on SQLAlchemy and Pydantic
- **asyncpg** (0.29.0+) - Async PostgreSQL driver
- **PostgreSQL** 15 - Database (via Docker)
- **Alembic** (1.12.1+) - Database migration tool

### AI/ML
- **Semantic Kernel** (0.9.0+) - AI orchestration framework
- **OpenAI** - AI service provider (configurable)

### Configuration
- **Pydantic Settings** (2.1.0+) - Settings management
- **python-dotenv** (1.0.0+) - Environment variable loading

### Authentication
- **python-jose** (3.3.0+) - JWT handling
- **passlib** (1.7.4+) - Password hashing

### Logging
- **structlog** (23.2.0+) - Structured logging

### Testing
- **pytest** (7.4.3+) - Testing framework
- **pytest-asyncio** (0.21.1+) - Async test support
- **httpx** (0.25.0+) - Async HTTP client for testing

### Development Tools
- **black** - Code formatter
- **ruff** - Fast linter
- **mypy** - Type checker

## Development Setup

### Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Installation
```bash
pip install -e ".[dev]"
```

### Database Setup
```bash
cd docker
docker-compose up -d
```

### Migrations
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Running
```bash
uvicorn app.main:app --reload
```

## Configuration Files

- `pyproject.toml` - Project metadata and dependencies
- `.env` - Environment variables (not in git)
- `.env.example` - Environment variable template
- `alembic.ini` - Alembic configuration

## Database Connection

- **URL Format**: `postgresql+asyncpg://user:password@host:port/dbname`
- **Default**: `postgresql+asyncpg://postgres:postgres@localhost:5432/interview_db`
- **Connection Pool**: Configured in `core/db.py`

## Environment Variables

Required in `.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `SEMANTIC_KERNEL_API_KEY` - AI service API key (optional)
- `DEBUG` - Debug mode flag
- `LOG_LEVEL` - Logging level

## Constraints

- Python 3.10+ required
- PostgreSQL 12+ required
- Async/await pattern throughout
- Type hints required for all functions

