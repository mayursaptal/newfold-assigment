# Use Python 3.12 for semantic-kernel compatibility
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies and Poetry in one layer to save space
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Configure Poetry: don't create virtual env (we're in container), don't ask interactive questions
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VENV_CREATE=true \
    PATH="/app/.venv/bin:$PATH"

# Copy Poetry configuration files
COPY pyproject.toml ./

# Install dependencies using Poetry (without lock file to get compatible versions)
RUN poetry install --with dev --no-root

# Copy application code and entrypoint script
COPY . .
COPY docker/entrypoint.sh /entrypoint.sh

# Install the application itself and set up entrypoint in one layer
RUN poetry install --only-root \
    && chmod +x /entrypoint.sh

# Expose ports
EXPOSE 8000
# Expose debugger port for remote debugging
EXPOSE 5678

# Use the smart entrypoint
ENTRYPOINT ["/entrypoint.sh"]

