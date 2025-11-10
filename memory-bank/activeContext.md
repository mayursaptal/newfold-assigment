# Active Context

## Current Work Focus

**Status**: Production-Ready System with Enhanced Features ✅

The project now implements a fully functional AI agent orchestration system using Semantic Kernel's `HandoffOrchestration` and `ChatCompletionAgent`, with recent enhancements including Poetry integration, comprehensive validation, and improved API functionality:

- **SearchAgent**: Handles film-related questions using native function plugins
- **LLMAgent**: Handles general questions using prompt-based plugins  
- **HandoffOrchestration**: Routes between agents using Semantic Kernel's native orchestration
- **Native Function Plugins**: Film search functionality exposed as kernel functions
- **Prompt-based Plugins**: LLM and summary generation using Semantic Kernel prompts
- **HandoffService**: Service layer managing orchestration lifecycle and response extraction

## Recent Changes

### Poetry Integration & Enhanced Validation (Latest)
- ✅ Integrated Poetry for modern dependency management and packaging
- ✅ Updated `pyproject.toml` with Poetry configuration and author information
- ✅ Enhanced Docker setup to use Poetry for faster, more reliable builds
- ✅ Added comprehensive Pydantic validation for Film models (release_year, rental_duration, etc.)
- ✅ Implemented robust error handling in API routes with specific validation messages
- ✅ Enhanced category filtering with case-insensitive partial matching using PostgreSQL ILIKE
- ✅ Added comprehensive test coverage for validation scenarios
- ✅ Updated all documentation to reflect Poetry usage and new features
- ✅ Fixed Python version compatibility issues (3.10-3.12 for semantic-kernel)

### Streamlined Docker Debug Configuration
- ✅ Implemented smart Docker entrypoint with environment-driven debug mode
- ✅ Removed complex debug shell scripts and separate compose files
- ✅ Added debugpy to dev dependencies for proper debug support
- ✅ Updated Cursor and VS Code launch configurations for direct connection
- ✅ Simplified tasks to use environment variables instead of scripts
- ✅ Created unified debug workflow for both Cursor and VS Code
- ✅ Enhanced Docker setup with automatic debug mode detection

### Comprehensive Documentation Update
- ✅ Added comprehensive docstrings to all Python modules
- ✅ Created package-level documentation for all layers (core, domain, api, app, plugins)
- ✅ Enhanced migration documentation with detailed upgrade/downgrade explanations
- ✅ Added inline comments for complex logic and business rules
- ✅ Documented all classes and functions following Google/NumPy docstring style
- ✅ Added usage examples and code snippets throughout
- ✅ Updated configuration file documentation (alembic.ini)

### Agent Architecture Refactoring
- ✅ Refactored `SearchAgent` to use `ChatCompletionAgent` with native function plugins
- ✅ Refactored `LLMAgent` to use `ChatCompletionAgent` with prompt-based plugins
- ✅ Replaced custom orchestration with Semantic Kernel's `HandoffOrchestration`
- ✅ Created `FilmSearchPlugin` as native function plugin for database queries
- ✅ Removed custom logic from agents (title extraction, conditional responses) - AI handles it
- ✅ Configured `OrchestrationHandoffs` for agent-to-agent transfers

### Plugin System
- ✅ Restructured plugins to match Semantic Kernel's expected format
- ✅ Native function plugins (`film_search`) for database operations
- ✅ Prompt-based plugins (`llm_agent`, `film_short_summary`) for AI operations
- ✅ Plugin loader uses Semantic Kernel's `add_plugin()` with `parent_directory`

### Project Structure
- ✅ Core infrastructure (`core/`)
- ✅ Domain layer (`domain/`)
- ✅ API layer (`api/v1/`)
- ✅ Application entry point (`app/main.py`)
- ✅ Agent orchestration (`app/agents/`)
- ✅ Plugin system (`plugins/`)
- ✅ Alembic migrations setup
- ✅ Docker configuration
- ✅ Test suite
- ✅ Configuration files

### Key Files Created
1. **Configuration**
   - `pyproject.toml` - Project dependencies
   - `.env` - Environment variables
   - `alembic.ini` - Migration config

2. **Core Infrastructure**
   - `core/settings.py` - Pydantic BaseSettings
   - `core/db.py` - Database setup
   - `core/dependencies.py` - Dependency injection
   - `core/ai_kernel.py` - Semantic Kernel factory
   - `core/auth.py` - Authentication
   - `core/logging.py` - Structured logging
   - `core/plugin_loader.py` - Semantic Kernel plugin registration

3. **Domain Layer**
   - `domain/models/` - SQLModel entities (Film, Category, Rental)
   - `domain/repositories/` - Repository pattern implementations
   - `domain/services/` - Business logic services
   - `domain/schemas/` - Pydantic schemas for API

4. **API Layer**
   - `api/v1/film_routes.py` - Film endpoints
   - `api/v1/rental_routes.py` - Rental endpoints
   - `api/v1/ai_routes.py` - AI endpoints with handoff orchestration
   - `api/v1/category_routes.py` - Category endpoints
   - `api/v1/customer_routes.py` - Customer endpoints

5. **Application**
   - `app/main.py` - FastAPI app
   - `app/agents/` - Agent implementations and orchestration
     - `search_agent.py` - Film search agent using ChatCompletionAgent
     - `llm_agent.py` - General question agent using ChatCompletionAgent
     - `orchestration.py` - HandoffOrchestration factory

6. **Plugins**
   - `plugins/film_search/` - Native function plugin for database queries
   - `plugins/llm_agent/` - Prompt-based plugin for general questions
   - `plugins/film_short_summary/` - Prompt-based plugin for summaries
   - `plugins/film_summary/` - Prompt-based plugin for detailed summaries
   - `plugins/chat/` - Prompt-based plugin for chat functionality

7. **Migrations**
   - `migrations/env.py` - Alembic environment
   - `migrations/script.py.mako` - Migration template
   - `migrations/versions/` - Database migration scripts

8. **Testing**
   - `tests/conftest.py` - Test fixtures
   - `tests/test_films.py` - Film tests
   - `tests/test_rentals.py` - Rental tests
   - `tests/test_ai.py` - AI agent tests
   - `tests/test_categories.py` - Category tests
   - `tests/test_customers.py` - Customer tests

9. **Docker**
   - `docker/docker-compose.yml` - PostgreSQL service
   - `docker/Dockerfile` - Application container

## Next Steps

### Immediate Actions
1. **Create `.env` file** (manually, as it's gitignored)
   - Copy from `.env.example`
   - Update with actual values (especially `OPENAI_API_KEY` for AI features)

2. **Start Application** (Choose one method)
   
   **Option A: Normal Mode**
   ```bash
   cd docker
   docker-compose up -d
   ```
   
   **Option B: Debug Mode (No Wait)**
   ```bash
   DEBUG_MODE=true DEBUG_WAIT=false docker-compose -f docker/docker-compose.yml up --build
   ```
   
   **Option C: Debug Mode (Wait for Debugger)**
   ```bash
   DEBUG_MODE=true DEBUG_WAIT=true docker-compose -f docker/docker-compose.yml up --build
   ```

3. **Run Initial Migration** (if needed)
   ```bash
   alembic upgrade head
   ```

4. **Test Application**
   ```bash
   curl -s http://localhost:8000/health
   ```

5. **Test AI Endpoints**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/ai/handoff" \
     -H "Content-Type: application/json" \
     -d '{"question": "tell me about Inception"}'
   ```

### Debug Workflow
1. **Start containers** with debug mode using environment variables
2. **Connect debugger** using Cursor or VS Code launch configurations
3. **Set breakpoints** and debug normally

### Future Enhancements
- Fine-tune handoff behavior between agents
- Add more native function plugins for other database operations
- Improve error handling in orchestration
- Add streaming responses for handoff endpoint
- Add more comprehensive tests for agent interactions
- Implement authentication endpoints
- Add request/response validation improvements
- Add rate limiting
- Add caching layer

## Active Decisions

### Architecture
- **Layered Architecture**: Chosen for clear separation of concerns
- **Dependency Injection**: Used throughout for testability
- **Repository Pattern**: Abstracted data access
- **Service Layer**: Business logic encapsulation

### Technology Choices
- **SQLModel**: Type-safe ORM with Pydantic integration
- **Semantic Kernel**: AI orchestration framework
- **structlog**: Structured JSON logging
- **pytest**: Testing framework with async support

### Configuration Strategy
- **Environment Variables**: Runtime configuration (`.env`)
- **Configuration**: All settings loaded from `.env` file via Pydantic BaseSettings

## Considerations

### Database
- Using async PostgreSQL driver (asyncpg)
- Connection pooling configured
- Migrations via Alembic

### AI Integration
- Semantic Kernel factory pattern
- ChatCompletionAgent for both SearchAgent and LLMAgent
- HandoffOrchestration for agent-to-agent routing
- Native function plugins for database operations
- Prompt-based plugins for LLM operations
- OrchestrationHandoffs configuration for handoff rules
- Configurable API keys and endpoints

### Testing
- In-memory SQLite for tests
- Dependency overrides for isolation
- Async test support

### Security
- JWT authentication ready
- Bearer token validation
- Secret key from environment

## Known Issues

### Handoff Behavior
- The handoff mechanism relies on the AI agent's interpretation of instructions
- SearchAgent must explicitly request handoff when no film is found
- LLMAgent is configured to NOT hand off to SearchAgent (one-way handoff)

### Plugin Loading
- Native function plugins must be registered before agent creation
- Prompt-based plugins are loaded automatically from `plugins/` directory
- Plugin structure must match Semantic Kernel's expected format

## Notes

- `.env` file is gitignored and must be created manually
- Semantic Kernel requires OpenAI API key to function (set `OPENAI_API_KEY` in `.env`)
- Database must be running before migrations/app startup
- All async operations use proper async/await patterns
- Agents are created within `create_handoff_orchestration()` factory function
- `InProcessRuntime` is used for agent execution in API context
- Agent responses are tracked via `agent_response_callback` to determine final agent

