# Docker with Poetry Integration

## Overview

The Docker setup has been updated to use Poetry for dependency management, providing better dependency resolution, faster builds, and reproducible environments.

## Key Features

### 🐍 **Python 3.12 Compatibility**
- Uses `python:3.12-slim` base image
- Compatible with semantic-kernel requirements (`<3.13`)
- Ensures consistent Python version across environments

### 📦 **Poetry Integration**
- Poetry installed via official installer
- Dependencies managed through `pyproject.toml` and `poetry.lock`
- Faster builds with Poetry caching
- Better dependency resolution

### 🚀 **Optimized Build Process**
1. **System Dependencies**: gcc, postgresql-client, curl
2. **Poetry Installation**: Official installer with symlink to `/usr/local/bin/poetry`
3. **Poetry Configuration**: No virtual env creation (container isolation)
4. **Dependency Installation**: `poetry install --with dev --no-root`
5. **Application Copy**: Copy source code
6. **Root Installation**: `poetry install --only-root`

## Docker Configuration

### Environment Variables

```bash
POETRY_NO_INTERACTION=1      # Don't ask interactive questions
POETRY_VENV_IN_PROJECT=0     # Don't create venv in project
POETRY_CACHE_DIR=/tmp/poetry_cache  # Cache location
POETRY_VENV_CREATE=false     # Don't create virtual environment
```

### Build Process

```dockerfile
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR

# Copy application and install
COPY . .
RUN poetry install --only-root
```

## Usage

### Basic Commands

```bash
# Build image
docker build -f docker/Dockerfile -t interview-api .

# Start services
cd docker && docker-compose up -d

# View Poetry info in container
docker exec interview_fastapi poetry show
docker exec interview_fastapi poetry check
```

### Development Workflow

```bash
# Start with auto-reload
cd docker && docker-compose up -d

# Run tests
docker exec interview_fastapi poetry run pytest tests/ -v

# Code quality
docker exec interview_fastapi poetry run black .
docker exec interview_fastapi poetry run ruff check .
docker exec interview_fastapi poetry run mypy . --config-file mypy.ini
```

## Benefits

### 🚀 **Performance**
- **Faster Builds**: Poetry cache reduces rebuild times
- **Parallel Installation**: Poetry installs dependencies in parallel
- **Optimized Layers**: Separate dependency and code layers

### 🔒 **Reliability**
- **Lock File**: `poetry.lock` ensures exact dependency versions
- **Dependency Resolution**: Poetry resolves conflicts automatically
- **Reproducible Builds**: Same dependencies across all environments

### 🛠 **Developer Experience**
- **Consistent Environment**: Same Python version (3.12) everywhere
- **Better Error Messages**: Poetry provides clear dependency conflict info
- **Modern Tooling**: Uses latest Python packaging standards

## Troubleshooting

### Common Issues

1. **Build Cache Issues**
   ```bash
   docker build --no-cache -f docker/Dockerfile -t interview-api .
   ```

2. **Poetry Lock File Missing**
   ```bash
   # Generate locally (requires Python 3.10-3.12)
   poetry lock
   ```

3. **Dependency Conflicts**
   ```bash
   # Check in container
   docker exec interview_fastapi poetry show --tree
   ```

### Debug Mode

The entrypoint script supports debug mode with Poetry:

```bash
# Debug mode with Poetry environment
DEBUG_MODE=true docker-compose up --build
```

## Migration Notes

### From pip to Poetry

The Docker setup maintains backward compatibility:
- Still supports `pip install -e ".[dev]"` if needed
- Poetry installation doesn't interfere with pip
- Can switch between methods if required

### Lock File Generation

Since the host may have Python 3.13+ (incompatible with semantic-kernel), the `poetry.lock` file is generated with relaxed constraints and works in the Python 3.12 container environment.

## Future Enhancements

- **Multi-stage builds**: Separate build and runtime stages
- **Poetry export**: Generate requirements.txt for pip compatibility
- **Dependency groups**: Separate test, dev, and prod dependencies
- **Build optimization**: Further reduce image size
