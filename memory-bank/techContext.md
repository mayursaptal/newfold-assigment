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
  - `ChatCompletionAgent` - AI agent implementation
  - `HandoffOrchestration` - Agent-to-agent routing
  - `OrchestrationHandoffs` - Handoff configuration
  - `InProcessRuntime` - Agent execution runtime
  - Native function plugins (`@kernel_function`)
  - Prompt-based plugins (from directory structure)
  - Response callback system for message tracking
  - Human response function for conversation flow
- **OpenAI** - AI service provider (configurable via `OPENAI_API_KEY`)
- **Azure OpenAI** - Alternative AI service provider (configurable)

### Configuration
- **Pydantic Settings** (2.1.0+) - Settings management
- **python-dotenv** (1.0.0+) - Environment variable loading
- **python-multipart** (0.0.6+) - Form data parsing support

### Authentication
- **python-jose[cryptography]** (3.3.0+) - JWT handling with cryptographic support
- **passlib[bcrypt]** (1.7.4+) - Password hashing with bcrypt support

### Logging
- **structlog** (23.2.0+) - Structured logging

### Testing
- **pytest** (7.4.3+) - Testing framework
- **pytest-asyncio** (0.21.1+) - Async test support
- **pytest-cov** (4.1.0+) - Test coverage reporting
- **httpx** (0.25.0+) - Async HTTP client for testing
- **aiosqlite** (0.19.0+) - In-memory SQLite for tests

### Development Tools
- **black** (23.11.0+) - Code formatter
- **ruff** (0.1.6+) - Fast linter and import sorter
- **mypy** (1.7.0+) - Type checker
- **pre-commit** (3.6.0+) - Git hooks for code quality
- **debugpy** (1.8.0+) - Python debugger for remote debugging

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

**Normal Mode:**
```bash
uvicorn app.main:app --reload
```

**Docker with Debug Mode:**
```bash
# Debug mode (no wait)
DEBUG_MODE=true DEBUG_WAIT=false docker-compose -f docker/docker-compose.yml up --build

# Debug mode (wait for debugger)
DEBUG_MODE=true DEBUG_WAIT=true docker-compose -f docker/docker-compose.yml up --build
```

## Configuration Files

- `pyproject.toml` - Project metadata and dependencies
- `.env` - Environment variables (not in git)
- `.env.example` - Environment variable template
- `alembic.ini` - Alembic configuration

## Docker Debug Configuration

### Smart Entrypoint
- `docker/entrypoint.sh` - Smart entrypoint script that detects debug mode
- Environment variable driven debug behavior
- Automatic debugpy setup when `DEBUG_MODE=true`

### Debug Environment Variables
- `DEBUG_MODE` - Enable/disable debug mode (default: false)
- `DEBUG_WAIT` - Wait for debugger attachment (default: false)  
- `DEBUG_PORT` - Debug server port (default: 5678)
- `APP_PORT` - FastAPI application port (default: 8000)

### IDE Integration
- `.cursor/launch.json` - Cursor debug configurations
- `.cursor/tasks.json` - Cursor tasks for container management
- `.vscode/launch.json` - VS Code debug configurations
- `.vscode/tasks.json` - VS Code tasks for container management

## Database Connection

- **URL Format**: `postgresql+asyncpg://user:password@host:port/dbname`
- **Default**: `postgresql+asyncpg://postgres:postgres@localhost:5432/interview_db`
- **Connection Pool**: Configured in `core/db.py`

## Environment Variables

Required in `.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `OPENAI_API_KEY` - OpenAI API key (required for AI features)
- `DEBUG` - Debug mode flag
- `LOG_LEVEL` - Logging level

## Constraints

- Python 3.10+ required
- PostgreSQL 12+ required
- Async/await pattern throughout
- Type hints required for all functions
- Semantic Kernel plugins must follow expected directory structure
- Native function plugins must be registered before agent creation
- OpenAI API key required for AI agent functionality
- Agent orchestration requires proper callback and response handling
- Response extraction must handle multiple message formats from Semantic Kernel
- Timeout handling required for orchestration operations (default: 30 seconds)
- debugpy required in dev dependencies for Docker debugging
- Docker containers must be started with appropriate environment variables for debug mode

## Semantic Kernel Plugin Structure

### Prompt-based Plugins
```
plugins/
    plugin_name/
        function_name/
            skprompt.txt          # Prompt template
            config.json           # Function configuration (optional)
```

### Native Function Plugins
```python
from semantic_kernel.functions import kernel_function

class MyPlugin:
    @kernel_function(
        name="function_name",
        description="Function description"
    )
    async def my_function(self, param: str) -> dict:
        # Implementation
        pass
```

Registration:
```python
plugin = MyPlugin(repository)
kernel.add_plugin(plugin, "plugin_name")
```

