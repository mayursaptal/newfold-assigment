# Debugging Guide

Comprehensive guide for debugging the Interview API using Docker, VS Code, Cursor, and various debugging techniques.

## 🐛 Debug Setup Overview

The Interview API includes a streamlined debugging system that works seamlessly with modern IDEs and supports both local and containerized debugging.

### Debug Architecture
```
IDE (VS Code/Cursor)
        │
        ▼ (Port 5678)
Docker Container
├── debugpy server
├── FastAPI app
└── Smart entrypoint
```

## 🚀 Quick Start Debugging

### 1. Start Debug Container
```bash
# Start in debug mode (no wait)
DEBUG_MODE=true DEBUG_WAIT=false docker-compose -f docker/docker-compose.yml up --build

# Start in debug mode (wait for debugger)
DEBUG_MODE=true DEBUG_WAIT=true docker-compose -f docker/docker-compose.yml up --build
```

### 2. Connect Debugger
- **VS Code**: Use "Debug FastAPI in Docker (Direct Connect)" configuration
- **Cursor**: Use "Debug FastAPI in Docker (Direct Connect)" configuration
- **Manual**: Connect to `localhost:5678` with debugpy protocol

### 3. Set Breakpoints and Debug
- Set breakpoints in your IDE
- Make API requests to trigger breakpoints
- Inspect variables and step through code

## 🔧 Environment Configuration

### Debug Environment Variables
```bash
# Enable debug mode
DEBUG_MODE=true

# Wait for debugger attachment (optional)
DEBUG_WAIT=false

# Debug server port (default: 5678)
DEBUG_PORT=5678

# Application port (default: 8000)
APP_PORT=8000
```

### Docker Compose Debug Setup
```yaml
# docker-compose.yml
services:
  fastapi:
    environment:
      DEBUG_MODE: ${DEBUG_MODE:-false}
      DEBUG_WAIT: ${DEBUG_WAIT:-false}
      DEBUG_PORT: ${DEBUG_PORT:-5678}
      APP_PORT: ${APP_PORT:-8000}
    ports:
      - "8000:8000"
      - "5678:5678"  # Debug port
```

## 🎯 IDE Configuration

### VS Code Configuration
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug FastAPI in Docker (Direct Connect)",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/app"
                }
            ],
            "justMyCode": false,
            "subProcess": true,
            "console": "integratedTerminal"
        },
        {
            "name": "Debug FastAPI Locally",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/app/main.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "DEBUG": "True",
                "LOG_LEVEL": "DEBUG",
                "DATABASE_URL": "postgresql+asyncpg://postgres:postgres@localhost:5432/interview_db"
            },
            "args": [],
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### Cursor Configuration
```json
// .cursor/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug FastAPI in Docker (Direct Connect)",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/app"
                }
            ],
            "justMyCode": false,
            "subProcess": true,
            "console": "integratedTerminal"
        }
    ]
}
```

### Tasks Configuration
```json
// .vscode/tasks.json or .cursor/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "docker-up-debug",
            "type": "shell",
            "command": "docker-compose",
            "args": ["-f", "docker/docker-compose.yml", "up", "--build"],
            "options": {
                "env": {
                    "DEBUG_MODE": "true",
                    "DEBUG_WAIT": "false"
                }
            },
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        }
    ]
}
```

## 🐳 Docker Debug Implementation

### Smart Entrypoint Script
```bash
#!/bin/bash
# docker/entrypoint.sh
set -e

# Default values
DEBUG_PORT=${DEBUG_PORT:-5678}
APP_PORT=${APP_PORT:-8000}
DEBUG_WAIT=${DEBUG_WAIT:-false}
DEBUG_MODE=${DEBUG_MODE:-false}

if [ "$DEBUG_MODE" = "true" ]; then
    echo "🐛 Starting FastAPI with debugger support..."
    echo "📍 Debug port: $DEBUG_PORT"
    echo "🌐 App port: $APP_PORT"
    echo "⏳ Wait for debugger: $DEBUG_WAIT"
    
    if [ "$DEBUG_WAIT" = "true" ]; then
        echo "⏳ Waiting for debugger to attach on port $DEBUG_PORT..."
        echo "🔗 Connect your debugger to localhost:$DEBUG_PORT"
        exec python -m debugpy --listen 0.0.0.0:$DEBUG_PORT --wait-for-client -m uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT --reload
    else
        echo "🚀 Starting with debugger listening (no wait)..."
        exec python -m debugpy --listen 0.0.0.0:$DEBUG_PORT -m uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT --reload
    fi
else
    echo "🚀 Starting FastAPI in normal mode..."
    exec uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT --reload
fi
```

### Dockerfile Debug Support
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including debugpy
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (includes debugpy in dev extras)
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY . .

# Copy and setup entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose application and debug ports
EXPOSE 8000 5678

ENTRYPOINT ["/entrypoint.sh"]
```

## 🔍 Debugging Techniques

### 1. Breakpoint Debugging
```python
# Set breakpoints in your IDE or use debugger statements
import debugpy

def some_function():
    # Programmatic breakpoint
    debugpy.breakpoint()
    
    # Your code here
    result = complex_operation()
    return result
```

### 2. Logging Debug Information
```python
import structlog

logger = structlog.get_logger()

async def debug_endpoint():
    logger.debug("Starting endpoint execution", endpoint="debug_endpoint")
    
    try:
        result = await some_async_operation()
        logger.debug("Operation completed", result=result)
        return result
    except Exception as e:
        logger.error("Operation failed", error=str(e), exc_info=True)
        raise
```

### 3. Database Query Debugging
```python
# Enable SQL query logging
from core.db import engine

# In settings.py
class Settings(BaseSettings):
    debug: bool = True
    db_echo: bool = True  # Enable SQL logging

# In db.py
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.db_echo,  # This will log all SQL queries
    pool_pre_ping=True
)
```

### 4. AI Agent Debugging
```python
# Debug AI agent interactions
class HandoffService:
    async def process_question(self, question: str) -> str:
        logger.debug("Processing AI question", question=question)
        
        # Add debug callback
        def debug_callback(agent, message):
            logger.debug(
                "Agent response",
                agent=agent.name,
                message_type=type(message).__name__,
                content=getattr(message, 'content', str(message))
            )
        
        # Execute with debugging
        async for response in self.orchestration.invoke_stream(
            kernel=self.kernel,
            chat_history=chat_history,
            agent_response_callback=debug_callback
        ):
            logger.debug("Stream response", response=response)
```

## 🧪 Testing and Debug Integration

### Debug Test Setup
```python
# tests/conftest.py
import pytest
import debugpy
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def debug_client():
    """Test client with debug support."""
    # Enable debugging for tests if needed
    if os.getenv("DEBUG_TESTS") == "true":
        debugpy.listen(("0.0.0.0", 5679))  # Different port for tests
        print("Debugger listening on port 5679 for tests")
    
    return TestClient(app)

@pytest.mark.asyncio
async def test_with_debugging(debug_client):
    """Example test with debugging support."""
    # Set breakpoint here if needed
    response = debug_client.get("/api/v1/films/")
    assert response.status_code == 200
```

### Debug Test Execution
```bash
# Run tests with debugging
DEBUG_TESTS=true pytest tests/test_films.py::test_specific_function -v -s

# Connect debugger to port 5679 for test debugging
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Debugger Not Connecting
**Problem**: IDE can't connect to debug port

**Solutions**:
```bash
# Check if debug port is accessible
telnet localhost 5678

# Verify container is running in debug mode
docker-compose logs fastapi | grep "debugger"

# Check port mapping
docker-compose ps
```

#### 2. Breakpoints Not Hitting
**Problem**: Breakpoints are ignored

**Solutions**:
- Verify path mappings in launch configuration
- Check that `justMyCode` is set to `false`
- Ensure source code matches container code
- Restart debugger connection

#### 3. Container Exits Immediately
**Problem**: Container stops right after starting

**Solutions**:
```bash
# Check container logs
docker-compose logs fastapi

# Verify entrypoint script permissions
docker-compose exec fastapi ls -la /entrypoint.sh

# Test entrypoint script manually
docker-compose exec fastapi /entrypoint.sh
```

#### 4. Database Connection Issues
**Problem**: Can't connect to database in debug mode

**Solutions**:
```bash
# Verify database is running
docker-compose ps postgres

# Check database connectivity
docker-compose exec fastapi pg_isready -h postgres -U postgres

# Verify environment variables
docker-compose exec fastapi env | grep DATABASE_URL
```

### Debug Port Conflicts
```bash
# If port 5678 is in use, change debug port
DEBUG_PORT=9999 docker-compose up --build

# Update IDE configuration to match new port
```

### Performance Debug Mode
```python
# Add performance monitoring to debug mode
import time
from functools import wraps

def debug_timing(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.debug(
            "Function execution time",
            function=func.__name__,
            execution_time=execution_time
        )
        
        return result
    return wrapper

@debug_timing
async def slow_function():
    # Your code here
    pass
```

## 📊 Debug Monitoring

### Debug Metrics Collection
```python
# Monitor debug sessions
class DebugMetrics:
    def __init__(self):
        self.breakpoint_hits = 0
        self.debug_sessions = 0
    
    def record_breakpoint(self):
        self.breakpoint_hits += 1
        logger.debug("Breakpoint hit", total_hits=self.breakpoint_hits)
    
    def start_session(self):
        self.debug_sessions += 1
        logger.info("Debug session started", session_count=self.debug_sessions)

debug_metrics = DebugMetrics()
```

### Health Check for Debug Mode
```python
@app.get("/debug/health")
async def debug_health():
    """Health check endpoint for debug mode."""
    return {
        "debug_mode": os.getenv("DEBUG_MODE", "false"),
        "debug_port": os.getenv("DEBUG_PORT", "5678"),
        "debugger_attached": debugpy.is_client_connected() if 'debugpy' in sys.modules else False
    }
```

## 🚀 Advanced Debugging

### Remote Debugging
```python
# For production debugging (use with caution)
import debugpy

if os.getenv("ENABLE_REMOTE_DEBUG") == "true":
    debugpy.listen(("0.0.0.0", 5678))
    print("Remote debugger enabled on port 5678")
```

### Conditional Debugging
```python
# Enable debugging based on conditions
def conditional_debug(condition: bool = False):
    if condition and os.getenv("DEBUG_MODE") == "true":
        debugpy.breakpoint()

# Usage
async def process_request(request_id: str):
    # Only debug specific requests
    conditional_debug(request_id == "debug-request-123")
```

### Memory Debugging
```python
import tracemalloc
import psutil
import os

def debug_memory():
    """Debug memory usage."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    logger.debug(
        "Memory usage",
        rss=memory_info.rss / 1024 / 1024,  # MB
        vms=memory_info.vms / 1024 / 1024   # MB
    )
    
    if tracemalloc.is_tracing():
        current, peak = tracemalloc.get_traced_memory()
        logger.debug(
            "Traced memory",
            current=current / 1024 / 1024,  # MB
            peak=peak / 1024 / 1024         # MB
        )
```

This comprehensive debugging guide ensures efficient development and troubleshooting of the Interview API across different environments and scenarios.
