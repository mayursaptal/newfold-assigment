# Technology Stack

The Interview API is built using modern Python technologies with a focus on performance, maintainability, and developer experience. This document provides a comprehensive overview of all technologies, frameworks, and tools used in the project.

## 🐍 Core Framework

### FastAPI (0.104.1+)
**Purpose**: Modern, fast web framework for building APIs

**Key Features**:
- Automatic API documentation (OpenAPI/Swagger)
- Built-in request/response validation
- Async/await support
- Type hints integration
- High performance (comparable to NodeJS and Go)

**Usage in Project**:
```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Interview API",
    description="FastAPI with AI agent orchestration",
    version="1.0.0"
)
```

**Benefits**:
- ✅ Automatic interactive documentation
- ✅ Type safety with Pydantic integration
- ✅ High performance async operations
- ✅ Modern Python features support

### Uvicorn (0.24.0+)
**Purpose**: ASGI server for running FastAPI applications

**Features**:
- Lightning-fast ASGI server
- Hot reload for development
- Production-ready performance
- WebSocket support

**Usage**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🗄️ Database Stack

### PostgreSQL 15
**Purpose**: Primary database for persistent data storage

**Features**:
- ACID compliance
- Advanced indexing
- JSON support
- Full-text search
- Robust concurrency control

**Configuration**:
```yaml
# docker-compose.yml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    POSTGRES_DB: interview_db
```

### SQLModel (0.0.14+)
**Purpose**: Type-safe ORM combining SQLAlchemy and Pydantic

**Key Benefits**:
- Single model definition for database and API
- Type safety with Python type hints
- Automatic validation
- FastAPI integration

**Example Usage**:
```python
from sqlmodel import SQLModel, Field, Relationship

class Film(SQLModel, table=True):
    __tablename__ = "film"
    
    film_id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    release_year: Optional[int] = Field(default=None)
    
    # Relationships
    category: Optional["Category"] = Relationship(back_populates="films")
```

### asyncpg (0.29.0+)
**Purpose**: High-performance async PostgreSQL driver

**Features**:
- Pure Python implementation
- Excellent performance
- Full async/await support
- Connection pooling

**Integration**:
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=True,
    pool_pre_ping=True
)
```

### Alembic (1.12.1+)
**Purpose**: Database migration tool for SQLAlchemy

**Features**:
- Version-controlled schema changes
- Automatic migration generation
- Rollback support
- Branch merging

**Usage**:
```bash
# Generate migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🤖 AI/ML Stack

### Semantic Kernel (0.9.0+)
**Purpose**: AI orchestration framework by Microsoft

**Key Components**:
- **ChatCompletionAgent**: AI agent implementation
- **HandoffOrchestration**: Agent-to-agent routing
- **Plugin System**: Extensible AI capabilities
- **Kernel Functions**: Native function integration

**Architecture**:
```python
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, HandoffOrchestration

# Create kernel
kernel = Kernel()

# Add AI service
kernel.add_service(OpenAIChatCompletion(...))

# Create agents
search_agent = ChatCompletionAgent(kernel=kernel, ...)
llm_agent = ChatCompletionAgent(kernel=kernel, ...)

# Setup orchestration
orchestration = HandoffOrchestration(agents=[search_agent, llm_agent])
```

### OpenAI Integration
**Purpose**: AI language model services

**Supported Models**:
- GPT-4 (default)
- GPT-3.5-turbo
- Custom fine-tuned models

**Configuration**:
```python
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

service = OpenAIChatCompletion(
    ai_model_id="gpt-4",
    api_key=settings.openai_api_key,
    org_id=settings.openai_org_id
)
```

## 🔧 Configuration & Settings

### Pydantic Settings (2.1.0+)
**Purpose**: Type-safe configuration management

**Features**:
- Environment variable loading
- Type validation
- Nested configuration
- Multiple source support

**Implementation**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
```

### python-dotenv (1.0.0+)
**Purpose**: Environment variable management

**Usage**:
```python
from dotenv import load_dotenv
load_dotenv()  # Load .env file
```

## 🔐 Security Stack

### python-jose[cryptography] (3.3.0+)
**Purpose**: JWT token handling with cryptographic support

**Features**:
- JWT encoding/decoding
- Cryptographic signatures
- Token validation
- Multiple algorithms support

**Implementation**:
```python
from jose import JWTError, jwt

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### passlib[bcrypt] (1.7.4+)
**Purpose**: Password hashing with bcrypt support

**Features**:
- Secure password hashing
- Salt generation
- Hash verification
- Multiple algorithms

**Usage**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)
```

## 📊 Logging & Monitoring

### structlog (23.2.0+)
**Purpose**: Structured logging for better observability

**Features**:
- JSON structured logs
- Contextual information
- Multiple output formats
- Performance optimized

**Configuration**:
```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if DEBUG else structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

## 🧪 Testing Stack

### pytest (7.4.3+)
**Purpose**: Primary testing framework

**Features**:
- Simple test syntax
- Powerful fixtures
- Plugin ecosystem
- Parallel execution

### pytest-asyncio (0.21.1+)
**Purpose**: Async test support for pytest

**Usage**:
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### pytest-cov (4.1.0+)
**Purpose**: Test coverage reporting

**Usage**:
```bash
pytest --cov=. --cov-report=html --cov-report=term
```

### httpx (0.25.0+)
**Purpose**: Async HTTP client for API testing

**Features**:
- Async/await support
- HTTP/2 support
- Request/response streaming
- Authentication support

**Testing Usage**:
```python
import httpx
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/films/")
        assert response.status_code == 200
```

### aiosqlite (0.19.0+)
**Purpose**: In-memory SQLite for testing

**Benefits**:
- Fast test execution
- Isolated test environment
- No external dependencies
- SQLAlchemy compatible

## 🛠️ Development Tools

### Code Quality Tools

#### black (23.11.0+)
**Purpose**: Opinionated code formatter

**Configuration**:
```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py310']
```

#### ruff (0.1.6+)
**Purpose**: Fast Python linter and import sorter

**Features**:
- Extremely fast (written in Rust)
- Replaces flake8, isort, and more
- Extensive rule set
- Auto-fixing capabilities

**Configuration**:
```toml
[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "W", "I", "N", "UP"]
```

#### mypy (1.7.0+)
**Purpose**: Static type checker

**Features**:
- Type hint validation
- Gradual typing support
- Plugin system
- IDE integration

**Configuration**:
```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Development Workflow

#### pre-commit (3.6.0+)
**Purpose**: Git hooks for code quality

**Configuration**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
```

### Debugging Tools

#### debugpy (1.8.0+)
**Purpose**: Python debugger for remote debugging

**Features**:
- Remote debugging support
- IDE integration
- Breakpoint support
- Variable inspection

**Docker Integration**:
```python
# In Docker entrypoint
if DEBUG_MODE:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    if DEBUG_WAIT:
        debugpy.wait_for_client()
```

## 🐳 Containerization

### Docker
**Purpose**: Application containerization

**Multi-stage Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY . .

# Smart entrypoint for debug support
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000 5678
ENTRYPOINT ["/entrypoint.sh"]
```

### Docker Compose
**Purpose**: Multi-container application orchestration

**Services**:
- PostgreSQL database
- FastAPI application
- Volume management
- Network configuration

## 📦 Package Management

### pyproject.toml
**Purpose**: Modern Python project configuration

**Structure**:
```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools-scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "interview"
version = "0.1.0"
description = "FastAPI with AI agent orchestration"
dependencies = [
    "fastapi>=0.104.1",
    "uvicorn[standard]>=0.24.0",
    "sqlmodel>=0.0.14",
    # ... more dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "black>=23.11.0",
    "ruff>=0.1.6",
    "mypy>=1.7.0",
    "debugpy>=1.8.0",
    # ... more dev dependencies
]
```

## 🚀 Performance Considerations

### Async/Await Stack
- **FastAPI**: Native async support
- **asyncpg**: Async database driver
- **httpx**: Async HTTP client
- **aiofiles**: Async file operations

### Connection Pooling
```python
# Database connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Caching Strategy
- **In-memory caching**: For frequently accessed data
- **Redis integration**: Ready for distributed caching
- **Query optimization**: Efficient database queries

## 📊 Monitoring & Observability

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "interview-api",
        "timestamp": datetime.utcnow()
    }
```

### Metrics Collection
- **Request/response times**
- **Database query performance**
- **AI agent response times**
- **Error rates and types**

## 🔄 Version Management

### Dependency Versions
All dependencies are pinned with minimum versions to ensure compatibility:

```toml
dependencies = [
    "fastapi>=0.104.1",      # Latest stable with security fixes
    "sqlmodel>=0.0.14",      # Type-safe ORM
    "semantic-kernel>=0.9.0", # AI orchestration
    "pydantic>=2.1.0",       # Data validation
]
```

### Python Version
- **Minimum**: Python 3.10
- **Recommended**: Python 3.11+
- **Features used**: Type hints, async/await, dataclasses

This technology stack provides a robust, scalable, and maintainable foundation for modern Python web applications with AI integration.
