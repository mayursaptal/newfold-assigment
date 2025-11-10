FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./

# Install Python dependencies (includes debugpy in dev extras)
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY . .

# Copy and set up entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 8000
# Expose debugger port for remote debugging
EXPOSE 5678

# Use the smart entrypoint
ENTRYPOINT ["/entrypoint.sh"]

