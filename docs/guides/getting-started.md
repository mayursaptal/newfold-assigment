# Getting Started Guide

Complete step-by-step guide to get the Interview API up and running on your local machine, from installation to making your first API calls.

## 🎯 Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Docker**: Latest version (recommended) or Docker Desktop
- **Git**: For cloning the repository
- **OpenAI API Key**: For AI features (optional for basic functionality)

### Recommended Tools
- **VS Code** or **Cursor**: For development and debugging
- **Postman** or **curl**: For API testing
- **pgAdmin** or **DBeaver**: For database management (optional)

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd interview

# Copy environment configuration
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file with your settings:
```bash
# Required for AI features
OPENAI_API_KEY=your_openai_api_key_here

# Database settings (defaults work for Docker)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/interview_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=interview_db

# Application settings
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-change-in-production
```

### 3. Start with Docker (Recommended)
```bash
cd docker
docker-compose up -d

# Wait for services to start (about 30 seconds)
# Check status
docker-compose ps
```

### 4. Verify Installation
```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"interview-api"}

# Access interactive documentation
open http://localhost:8000/docs
```

### 5. Test AI Features
```bash
# Test AI agent interaction
curl -X POST "http://localhost:8000/api/v1/ai/handoff" \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me about action movies"}'
```

🎉 **Congratulations!** Your Interview API is now running!

## 📋 Detailed Setup Options

### Option 1: Docker Setup (Recommended)

#### Advantages
- ✅ No local Python setup required
- ✅ Consistent environment across systems
- ✅ Includes PostgreSQL database
- ✅ Easy debugging support
- ✅ Production-like setup

#### Step-by-Step
```bash
# 1. Ensure Docker is running
docker --version
docker-compose --version

# 2. Clone repository
git clone <repository-url>
cd interview

# 3. Environment setup
cp .env.example .env
# Edit .env with your OpenAI API key

# 4. Start services
cd docker
docker-compose up -d

# 5. Check logs (optional)
docker-compose logs -f

# 6. Verify services
docker-compose ps
curl http://localhost:8000/health
```

#### Docker Services
- **FastAPI App**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **API Documentation**: http://localhost:8000/docs

### Option 2: Local Development Setup

#### Advantages
- ✅ Faster development cycle
- ✅ Direct Python debugging
- ✅ Full control over environment
- ✅ IDE integration

#### Prerequisites
```bash
# Install Python 3.11+
python --version  # Should be 3.11+

# Install PostgreSQL locally or use Docker for DB only
# Option A: Local PostgreSQL
brew install postgresql  # macOS
sudo apt install postgresql  # Ubuntu

# Option B: Docker PostgreSQL only
cd docker
docker-compose up postgres -d
```

#### Step-by-Step
```bash
# 1. Clone and navigate
git clone <repository-url>
cd interview

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Environment setup
cp .env.example .env
# Edit .env with your configuration

# 5. Database setup (if using local PostgreSQL)
createdb interview_db
psql interview_db < sql/01-pagila-schema.sql
psql interview_db < sql/02-pagila-data.sql

# 6. Run migrations
alembic upgrade head

# 7. Start application
uvicorn app.main:app --reload

# 8. Verify
curl http://localhost:8000/health
```

## 🗄️ Database Setup

### Automatic Setup (Docker)
When using Docker, the database is automatically:
- Created with proper schema
- Populated with sample data (Pagila dataset)
- Configured with optimal settings

### Manual Database Setup
```bash
# 1. Create database
createdb interview_db

# 2. Load schema
psql interview_db < sql/01-pagila-schema.sql

# 3. Load sample data
psql interview_db < sql/02-pagila-data.sql

# 4. Run migrations
alembic upgrade head

# 5. Verify data
psql interview_db -c "SELECT COUNT(*) FROM film;"
# Should return ~1000 films
```

### Database Contents
After setup, your database will contain:
- **1,000+ Films** with metadata
- **16 Categories** (Action, Comedy, Drama, etc.)
- **200+ Actors** with film relationships
- **600+ Customers** with rental history
- **16,000+ Rental records**

## 🔑 API Key Configuration

### OpenAI API Key Setup
1. **Get API Key**:
   - Visit https://platform.openai.com/api-keys
   - Create new API key
   - Copy the key (starts with `sk-`)

2. **Configure in .env**:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
   ```

3. **Verify Configuration**:
   ```bash
   # Test AI endpoint
   curl -X POST "http://localhost:8000/api/v1/ai/handoff" \
     -H "Content-Type: application/json" \
     -d '{"question": "Hello, can you help me?"}'
   ```

### Without OpenAI API Key
The API works without an OpenAI key, but AI features will be disabled:
- ✅ Film CRUD operations
- ✅ Category management
- ✅ Rental operations
- ✅ Database queries
- ❌ AI agent interactions
- ❌ Intelligent recommendations

## 🧪 Testing Your Setup

### 1. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"interview-api"}
```

### 2. API Documentation
Visit http://localhost:8000/docs to see interactive API documentation.

### 3. Basic API Tests
```bash
# Get all films
curl http://localhost:8000/api/v1/films/ | jq '.[0]'

# Get specific film
curl http://localhost:8000/api/v1/films/1 | jq

# Get categories
curl http://localhost:8000/api/v1/categories/ | jq
```

### 4. AI Features Test
```bash
# Test AI agent (requires OpenAI API key)
curl -X POST "http://localhost:8000/api/v1/ai/handoff" \
  -H "Content-Type: application/json" \
  -d '{"question": "Recommend some sci-fi movies"}' | jq
```

### 5. Database Test
```bash
# Using Docker
docker-compose exec postgres psql -U postgres -d interview_db -c "SELECT title FROM film LIMIT 5;"

# Using local PostgreSQL
psql interview_db -c "SELECT title FROM film LIMIT 5;"
```

## 🐛 Development and Debugging

### Enable Debug Mode
```bash
# Start with debugging enabled
DEBUG_MODE=true DEBUG_WAIT=false docker-compose up --build

# Connect debugger to localhost:5678
```

### IDE Setup
1. **VS Code**: Use provided `.vscode/launch.json`
2. **Cursor**: Use provided `.cursor/launch.json`
3. **Set breakpoints** and debug normally

### Hot Reload
Both Docker and local setups support hot reload:
- Code changes automatically restart the server
- No need to manually restart during development

## 📊 Monitoring and Logs

### View Logs
```bash
# Docker logs
docker-compose logs -f fastapi
docker-compose logs -f postgres

# Local logs
# Logs appear in terminal where uvicorn is running
```

### Log Levels
Configure in `.env`:
```bash
LOG_LEVEL=DEBUG  # Most verbose
LOG_LEVEL=INFO   # Standard
LOG_LEVEL=WARNING  # Warnings and errors only
```

### Structured Logging
Logs are in JSON format for production:
```json
{
  "event": "Request completed",
  "method": "GET",
  "path": "/api/v1/films/",
  "status_code": 200,
  "duration": 0.045,
  "timestamp": "2024-11-10T10:30:00Z"
}
```

## 🔧 Common Configuration

### Environment Variables Reference
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=interview_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Application
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key
API_V1_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

# AI Configuration
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4
OPENAI_ORG_ID=your-org-id  # Optional

# Debug Configuration
DEBUG_MODE=false
DEBUG_WAIT=false
DEBUG_PORT=5678
```

### Port Configuration
Default ports used:
- **8000**: FastAPI application
- **5432**: PostgreSQL database
- **5678**: Debug server (when enabled)

Change ports if needed:
```bash
# In docker-compose.yml
ports:
  - "9000:8000"  # Map to port 9000 instead
  - "5433:5432"  # Map to port 5433 instead
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Error: Port 8000 is already in use
# Solution: Change port or stop conflicting service
lsof -i :8000  # Find what's using port 8000
kill -9 <PID>  # Stop the process

# Or change port in docker-compose.yml
ports:
  - "9000:8000"
```

#### 2. Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection manually
docker-compose exec postgres psql -U postgres -d interview_db
```

#### 3. OpenAI API Errors
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Test API key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### 4. Permission Denied
```bash
# Docker permission issues (Linux)
sudo usermod -aG docker $USER
# Log out and back in

# File permission issues
chmod +x docker/entrypoint.sh
```

### Getting Help
1. **Check logs**: `docker-compose logs -f`
2. **Verify environment**: `docker-compose exec fastapi env`
3. **Test components individually**: Use health endpoints
4. **Check documentation**: Visit `/docs` endpoint
5. **Review configuration**: Verify `.env` file

## 🎓 Next Steps

### Learn the API
1. **Explore Documentation**: http://localhost:8000/docs
2. **Try Examples**: See [API Examples](../api/examples.md)
3. **Understand Architecture**: Read [Architecture Guide](../architecture/overview.md)

### Development Workflow
1. **Set up debugging**: Follow [Debugging Guide](../development/debugging.md)
2. **Write tests**: See [Testing Guide](../development/testing.md)
3. **Code quality**: Use pre-commit hooks

### Deployment
1. **Production setup**: See [Deployment Guide](../deployment/docker.md)
2. **Security**: Review security best practices
3. **Monitoring**: Set up logging and metrics

### AI Features
1. **Understand agents**: Read [AI Agents Guide](../architecture/agents.md)
2. **Create plugins**: See [Plugin Development](../architecture/plugins.md)
3. **Customize behavior**: Modify agent instructions

You're now ready to start developing with the Interview API! 🚀
