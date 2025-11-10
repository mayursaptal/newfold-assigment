# Docker Deployment Guide

Complete guide for deploying the Interview API using Docker and Docker Compose, including development, staging, and production configurations.

## 🐳 Docker Overview

### Container Architecture
```
┌─────────────────────────────────────────┐
│              Load Balancer               │
│                (Optional)                │
└─────────────────────────────────────────┘
                     │
┌─────────────────────────────────────────┐
│            FastAPI Container            │
│  ┌─────────────────────────────────┐   │
│  │         Interview API           │   │
│  │    (Python 3.11 + FastAPI)     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
                     │
┌─────────────────────────────────────────┐
│          PostgreSQL Container           │
│  ┌─────────────────────────────────┐   │
│  │        PostgreSQL 15            │   │
│  │     (with Pagila data)          │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Key Features
- **Multi-stage builds** for optimized images
- **Smart entrypoint** with debug mode detection
- **Health checks** for container monitoring
- **Volume persistence** for database data
- **Network isolation** with custom networks
- **Environment-based configuration**

## 📁 Docker Files Structure

```
docker/
├── Dockerfile              # Multi-stage application image
├── docker-compose.yml      # Development/production compose
├── entrypoint.sh          # Smart entrypoint script
└── .dockerignore          # Docker ignore patterns
```

## 🏗️ Dockerfile Analysis

### Multi-Stage Build
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY . .

# Copy and setup entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 8000 5678

# Use smart entrypoint
ENTRYPOINT ["/entrypoint.sh"]
```

### Smart Entrypoint Features
```bash
#!/bin/bash
set -e

# Environment variable detection
DEBUG_MODE=${DEBUG_MODE:-false}
DEBUG_WAIT=${DEBUG_WAIT:-false}
DEBUG_PORT=${DEBUG_PORT:-5678}
APP_PORT=${APP_PORT:-8000}

# Conditional startup based on environment
if [ "$DEBUG_MODE" = "true" ]; then
    # Debug mode with debugpy
    python -m debugpy --listen 0.0.0.0:$DEBUG_PORT -m uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT --reload
else
    # Production mode
    uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT --reload
fi
```

## 🚀 Quick Deployment

### Development Deployment
```bash
# Clone repository
git clone <repository-url>
cd interview

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Start services
cd docker
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f fastapi
```

### Production Deployment
```bash
# Production environment setup
export DEBUG_MODE=false
export DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/interview_db
export OPENAI_API_KEY=your_production_key

# Deploy with production settings
docker-compose -f docker-compose.yml up -d --build
```

## 🔧 Docker Compose Configuration

### Development Configuration
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    container_name: interview_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: interview_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ../sql:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - interview_network

  fastapi:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: interview_fastapi
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/interview_db
      DEBUG: ${DEBUG:-True}
      DEBUG_MODE: ${DEBUG_MODE:-false}
      DEBUG_WAIT: ${DEBUG_WAIT:-false}
      DEBUG_PORT: ${DEBUG_PORT:-5678}
      APP_PORT: ${APP_PORT:-8000}
      OPENAI_API_KEY: ${OPENAI_API_KEY:-}
    env_file:
      - ../.env
    ports:
      - "8000:8000"
      - "5678:5678"  # Debug port
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - interview_network
    volumes:
      - ../:/app  # Development volume mount
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local

networks:
  interview_network:
    driver: bridge
```

### Production Configuration
```yaml
# docker-compose.prod.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - interview_network
    # No port exposure for security

  fastapi:
    build:
      context: .
      dockerfile: docker/Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      DEBUG: false
      DEBUG_MODE: false
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - interview_network
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🐛 Debug Mode Deployment

### Debug Mode Options
```bash
# Option 1: No wait (app starts immediately)
DEBUG_MODE=true DEBUG_WAIT=false docker-compose up --build

# Option 2: Wait for debugger
DEBUG_MODE=true DEBUG_WAIT=true docker-compose up --build

# Option 3: Custom debug port
DEBUG_MODE=true DEBUG_PORT=9999 docker-compose up --build
```

### Debugger Connection
```bash
# Check debug port is accessible
telnet localhost 5678

# Connect with VS Code/Cursor
# Use "Debug FastAPI in Docker (Direct Connect)" configuration
# Host: localhost, Port: 5678
```

### Debug Logs
```bash
# Monitor debug startup
docker-compose logs -f fastapi

# Expected output:
# 🐛 Starting FastAPI with debugger support...
# 📍 Debug port: 5678
# 🌐 App port: 8000
# ⏳ Wait for debugger: false
# 🚀 Starting with debugger listening (no wait)...
```

## 🔍 Container Management

### Basic Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build -d

# View logs
docker-compose logs -f
docker-compose logs -f fastapi
docker-compose logs -f postgres

# Check status
docker-compose ps

# Execute commands in container
docker-compose exec fastapi bash
docker-compose exec postgres psql -U postgres -d interview_db
```

### Container Inspection
```bash
# Inspect container
docker inspect interview_fastapi

# Check resource usage
docker stats interview_fastapi interview_postgres

# View container processes
docker-compose top

# Check networks
docker network ls
docker network inspect docker_interview_network
```

## 📊 Health Monitoring

### Health Check Configuration
```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Health Check Commands
```bash
# Check container health
docker-compose ps
docker inspect --format='{{.State.Health.Status}}' interview_fastapi

# Manual health check
curl http://localhost:8000/health

# Database health check
docker-compose exec postgres pg_isready -U postgres
```

### Monitoring Scripts
```bash
#!/bin/bash
# health-check.sh
set -e

echo "Checking application health..."

# Check FastAPI health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FastAPI is healthy"
else
    echo "❌ FastAPI is unhealthy"
    exit 1
fi

# Check database connectivity
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL is unhealthy"
    exit 1
fi

echo "🎉 All services are healthy"
```

## 🔒 Security Configuration

### Production Security
```yaml
# docker-compose.prod.yml security enhancements
services:
  postgres:
    # Don't expose database port
    # ports: []
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
    secrets:
      - postgres_password
    
  fastapi:
    # Run as non-root user
    user: "1000:1000"
    # Read-only root filesystem
    read_only: true
    # Temporary filesystem for writable areas
    tmpfs:
      - /tmp
      - /var/tmp
    # Security options
    security_opt:
      - no-new-privileges:true
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt
```

### Environment Security
```bash
# Use Docker secrets for sensitive data
echo "secure_password" | docker secret create postgres_password -

# Or use external secret management
export POSTGRES_PASSWORD=$(vault kv get -field=password secret/postgres)
```

## 📈 Performance Optimization

### Image Optimization
```dockerfile
# Multi-stage build for smaller images
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --user -e ".[dev]"

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
```

### Resource Limits
```yaml
services:
  fastapi:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    
  postgres:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Database Optimization
```yaml
postgres:
  environment:
    POSTGRES_SHARED_PRELOAD_LIBRARIES: pg_stat_statements
    POSTGRES_MAX_CONNECTIONS: 100
    POSTGRES_SHARED_BUFFERS: 256MB
    POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
```

## 🔄 Backup and Recovery

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres interview_db > backup.sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U postgres interview_db > "${BACKUP_DIR}/interview_db_${DATE}.sql"
gzip "${BACKUP_DIR}/interview_db_${DATE}.sql"
```

### Database Restore
```bash
# Restore from backup
docker-compose exec -T postgres psql -U postgres interview_db < backup.sql

# Or using docker cp
docker cp backup.sql interview_postgres:/tmp/
docker-compose exec postgres psql -U postgres interview_db -f /tmp/backup.sql
```

### Volume Backup
```bash
# Backup volume data
docker run --rm -v docker_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .

# Restore volume data
docker run --rm -v docker_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data
```

## 🚀 Scaling and Load Balancing

### Horizontal Scaling
```yaml
# docker-compose.scale.yml
services:
  fastapi:
    deploy:
      replicas: 3
    ports: []  # Remove direct port mapping
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - fastapi
```

### Load Balancer Configuration
```nginx
# nginx.conf
upstream fastapi_backend {
    server interview_fastapi_1:8000;
    server interview_fastapi_2:8000;
    server interview_fastapi_3:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /health {
        access_log off;
        proxy_pass http://fastapi_backend;
    }
}
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Secrets properly managed
- [ ] Database migrations ready
- [ ] SSL certificates prepared (if needed)
- [ ] Backup strategy implemented
- [ ] Monitoring configured

### Deployment Steps
- [ ] Build and test images locally
- [ ] Deploy to staging environment
- [ ] Run integration tests
- [ ] Deploy to production
- [ ] Verify health checks
- [ ] Monitor logs and metrics

### Post-Deployment
- [ ] Verify all endpoints working
- [ ] Check database connectivity
- [ ] Test AI functionality
- [ ] Monitor performance metrics
- [ ] Set up alerting
- [ ] Document deployment

This comprehensive Docker deployment guide ensures reliable, secure, and scalable deployment of the Interview API in any environment.
