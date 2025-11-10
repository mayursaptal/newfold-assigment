# Use Python 3.12 for semantic-kernel compatibility
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including curl for Poetry installation
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Configure Poetry: don't create virtual env (we're in container), don't ask interactive questions
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VENV_CREATE=false

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Install dependencies using Poetry
RUN poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Install the application itself
RUN poetry install --only-root

# Copy and set up entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 8000
# Expose debugger port for remote debugging
EXPOSE 5678

# Use the smart entrypoint
ENTRYPOINT ["/entrypoint.sh"]

