# Dependencies & Requirements

This document provides detailed information about all project dependencies, their versions, purposes, and relationships.

## 📋 Dependency Overview

### Dependency Categories
- **Core Framework**: FastAPI, Uvicorn, Pydantic
- **Database**: SQLModel, asyncpg, Alembic
- **AI/ML**: Semantic Kernel, OpenAI
- **Security**: JWT, bcrypt, cryptography
- **Development**: Testing, linting, formatting tools
- **Infrastructure**: Logging, configuration, Docker

## 🎯 Production Dependencies

### Web Framework
```toml
fastapi = ">=0.104.1"
uvicorn = {extras = ["standard"], version = ">=0.24.0"}
```

**FastAPI (0.104.1+)**
- Modern, fast web framework
- Automatic API documentation
- Built-in validation and serialization
- High performance async support

**Uvicorn (0.24.0+)**
- ASGI server implementation
- Production-ready performance
- Hot reload for development
- WebSocket support

### Database Stack
```toml
sqlmodel = ">=0.0.14"
asyncpg = ">=0.29.0"
alembic = ">=1.12.1"
```

**SQLModel (0.0.14+)**
- Type-safe ORM combining SQLAlchemy + Pydantic
- Single model definition for DB and API
- Automatic validation and serialization
- FastAPI integration

**asyncpg (0.29.0+)**
- High-performance async PostgreSQL driver
- Pure Python implementation
- Connection pooling support
- Excellent performance characteristics

**Alembic (1.12.1+)**
- Database migration tool for SQLAlchemy
- Version-controlled schema changes
- Automatic migration generation
- Rollback and branching support

### AI/ML Framework
```toml
semantic-kernel = ">=0.9.0"
```

**Semantic Kernel (0.9.0+)**
- AI orchestration framework by Microsoft
- Agent-based architecture
- Plugin system for extensibility
- Multi-model support (OpenAI, Azure, etc.)

**Key Components**:
- `ChatCompletionAgent`: AI agent implementation
- `HandoffOrchestration`: Agent routing system
- `Kernel`: Core AI service container
- Plugin system for custom functions

### Data Validation & Serialization
```toml
pydantic = ">=2.1.0"
pydantic-settings = ">=2.1.0"
```

**Pydantic (2.1.0+)**
- Data validation using Python type hints
- JSON serialization/deserialization
- Settings management
- Error handling and reporting

**Pydantic Settings (2.1.0+)**
- Environment-based configuration
- Type-safe settings management
- Multiple source support (.env, environment variables)
- Validation and documentation

### Security
```toml
python-jose = {extras = ["cryptography"], version = ">=3.3.0"}
passlib = {extras = ["bcrypt"], version = ">=1.7.4"}
python-multipart = ">=0.0.6"
```

**python-jose[cryptography] (3.3.0+)**
- JWT token creation and validation
- Cryptographic signature support
- Multiple algorithm support
- Security best practices

**passlib[bcrypt] (1.7.4+)**
- Password hashing library
- bcrypt algorithm support
- Salt generation and verification
- Secure password storage

**python-multipart (0.0.6+)**
- Form data parsing support
- File upload handling
- Multipart request processing
- FastAPI integration

### Configuration & Environment
```toml
python-dotenv = ">=1.0.0"
```

**python-dotenv (1.0.0+)**
- Environment variable loading from .env files
- Development configuration management
- Production environment support
- Cross-platform compatibility

### Logging
```toml
structlog = ">=23.2.0"
```

**structlog (23.2.0+)**
- Structured logging library
- JSON output for production
- Contextual log information
- High performance logging

### HTTP Client
```toml
httpx = ">=0.25.0"
```

**httpx (0.25.0+)**
- Modern async HTTP client
- HTTP/2 support
- Request/response streaming
- Testing integration

## 🧪 Development Dependencies

### Testing Framework
```toml
pytest = ">=7.4.3"
pytest-asyncio = ">=0.21.1"
pytest-cov = ">=4.1.0"
aiosqlite = ">=0.19.0"
```

**pytest (7.4.3+)**
- Modern Python testing framework
- Fixture system for test setup
- Plugin ecosystem
- Parallel test execution

**pytest-asyncio (0.21.1+)**
- Async/await support for pytest
- Async fixture support
- Event loop management
- Async test discovery

**pytest-cov (4.1.0+)**
- Test coverage measurement
- HTML and terminal reports
- Branch coverage analysis
- Integration with pytest

**aiosqlite (0.19.0+)**
- Async SQLite driver for testing
- In-memory database support
- Fast test execution
- SQLAlchemy compatibility

### Code Quality Tools
```toml
black = ">=23.11.0"
ruff = ">=0.1.6"
mypy = ">=1.7.0"
pre-commit = ">=3.6.0"
```

**black (23.11.0+)**
- Opinionated code formatter
- Consistent code style
- Fast formatting
- IDE integration

**ruff (0.1.6+)**
- Fast Python linter (written in Rust)
- Replaces flake8, isort, and more
- Auto-fixing capabilities
- Extensive rule set

**mypy (1.7.0+)**
- Static type checker
- Type hint validation
- Gradual typing support
- IDE integration

**pre-commit (3.6.0+)**
- Git hooks for code quality
- Automated code checks
- Multi-language support
- CI/CD integration

### Debugging
```toml
debugpy = ">=1.8.0"
```

**debugpy (1.8.0+)**
- Python debugger for remote debugging
- IDE integration (VS Code, Cursor)
- Breakpoint support
- Variable inspection

## 🔗 Dependency Relationships

### Core Framework Dependencies
```
FastAPI
├── Pydantic (data validation)
├── Starlette (ASGI framework)
└── Uvicorn (ASGI server)

SQLModel
├── SQLAlchemy (ORM core)
├── Pydantic (validation)
└── asyncpg (PostgreSQL driver)
```

### AI Stack Dependencies
```
Semantic Kernel
├── OpenAI (AI service)
├── Pydantic (data models)
├── httpx (HTTP client)
└── numpy (numerical operations)
```

### Security Stack Dependencies
```
Authentication
├── python-jose (JWT handling)
├── passlib (password hashing)
└── cryptography (crypto operations)
```

## 📊 Version Compatibility Matrix

| Component | Python 3.10 | Python 3.11 | Python 3.12 |
|-----------|--------------|--------------|--------------|
| FastAPI   | ✅ | ✅ | ✅ |
| SQLModel  | ✅ | ✅ | ✅ |
| Semantic Kernel | ✅ | ✅ | ⚠️ |
| pytest    | ✅ | ✅ | ✅ |
| mypy      | ✅ | ✅ | ✅ |

**Legend**:
- ✅ Fully supported
- ⚠️ Limited support or beta
- ❌ Not supported

## 🔧 Installation Methods

### Standard Installation
```bash
# Install production dependencies
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Docker Installation
```dockerfile
# Dependencies are installed in Dockerfile
RUN pip install --no-cache-dir -e ".[dev]"
```

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## 🚨 Security Considerations

### Dependency Security
- **Regular Updates**: Dependencies are regularly updated for security patches
- **Vulnerability Scanning**: Use tools like `safety` or `pip-audit`
- **Pinned Versions**: Minimum versions specified to ensure security fixes
- **Trusted Sources**: All dependencies from PyPI with verification

### Security-Critical Dependencies
```toml
# These dependencies handle sensitive operations
python-jose = {extras = ["cryptography"], version = ">=3.3.0"}  # JWT security
passlib = {extras = ["bcrypt"], version = ">=1.7.4"}           # Password hashing
cryptography = ">=3.4.0"                                       # Crypto operations
```

## 📈 Performance Impact

### High-Performance Dependencies
- **asyncpg**: Fastest PostgreSQL driver for Python
- **uvicorn**: High-performance ASGI server
- **ruff**: Extremely fast linting (Rust-based)
- **FastAPI**: One of the fastest Python web frameworks

### Memory Usage
| Component | Memory Impact | Notes |
|-----------|---------------|-------|
| FastAPI | Low | Efficient request handling |
| SQLModel | Medium | ORM overhead |
| Semantic Kernel | Medium-High | AI model loading |
| pytest | Low | Testing only |

## 🔄 Dependency Management

### Update Strategy
```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package_name

# Update all packages (use with caution)
pip install --upgrade -r requirements.txt
```

### Version Pinning Strategy
- **Minimum versions**: Specified for all dependencies
- **Compatible releases**: Using `>=` for flexibility
- **Security updates**: Regular monitoring and updates
- **Breaking changes**: Careful evaluation before major version updates

### Dependency Resolution
```bash
# Generate lock file
pip freeze > requirements.lock

# Install from lock file
pip install -r requirements.lock
```

## 🧪 Testing Dependencies

### Test-Specific Dependencies
```toml
# Only needed for testing
aiosqlite = ">=0.19.0"      # In-memory SQLite for tests
pytest-cov = ">=4.1.0"     # Coverage reporting
httpx = ">=0.25.0"          # HTTP client for API tests
```

### Test Database Setup
```python
# Using aiosqlite for fast test execution
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Test-specific engine configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL logging in tests
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)
```

## 🔍 Dependency Analysis

### Bundle Size Analysis
```bash
# Analyze installed packages
pip show package_name

# List all dependencies
pip list

# Dependency tree
pip install pipdeptree
pipdeptree
```

### Unused Dependencies
```bash
# Find unused dependencies
pip install pip-check
pip-check

# Or use pipreqs to generate requirements from imports
pip install pipreqs
pipreqs . --force
```

## 📋 Maintenance Checklist

### Regular Maintenance Tasks
- [ ] Update dependencies monthly
- [ ] Check security advisories
- [ ] Run vulnerability scans
- [ ] Update Docker base images
- [ ] Review and update version pins
- [ ] Test compatibility with new versions
- [ ] Update documentation

### Monitoring Tools
- **Dependabot**: Automated dependency updates
- **Safety**: Security vulnerability scanning
- **pip-audit**: PyPI package vulnerability scanner
- **Snyk**: Comprehensive security monitoring

This dependency management strategy ensures security, performance, and maintainability while providing flexibility for future updates and enhancements.
