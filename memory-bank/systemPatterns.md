# System Patterns

## Architecture Pattern

### Layered Architecture with Dependency Injection

The project follows a **layered architecture** pattern inspired by pagila_api:

```
┌─────────────────────────────────────┐
│         app/ (Entry Point)          │
│      FastAPI initialization         │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│      api/v1/ (Presentation)         │
│      HTTP routes & validation       │
└─────────────────────────────────────┘
                  │
                  ▼ (Dependency Injection)
┌─────────────────────────────────────┐
│      domain/ (Business Logic)       │
│  ┌──────────┐  ┌──────────────┐   │
│  │ Services │  │ Repositories │   │
│  └──────────┘  └──────────────┘   │
│  ┌──────────────────────────────┐  │
│  │        Models (SQLModel)     │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│      core/ (Infrastructure)        │
│  Database │ Auth │ AI │ Logging    │
└─────────────────────────────────────┘
```

## Key Design Patterns

### 1. Dependency Injection

FastAPI's dependency injection system is used throughout:

- **Database Sessions**: Injected via `get_db_session()`
- **Repositories**: Injected via `get_*_repository()`
- **Services**: Injected via `get_*_service()`
- **AI Kernel**: Injected via `get_ai_kernel()`

**Location**: `core/dependencies.py`

**Example**:
```python
@router.get("/films")
async def get_films(
    service: FilmService = Depends(get_film_service)
):
    return await service.get_films()
```

### 2. Repository Pattern

Data access is abstracted through repositories:

- **FilmRepository**: Film data access
- **RentalRepository**: Rental data access

**Location**: `domain/repositories.py`

**Benefits**:
- Separation of concerns
- Easy to test (mock repositories)
- Database-agnostic business logic

### 3. Service Layer Pattern

Business logic is encapsulated in services:

- **FilmService**: Film business logic
- **RentalService**: Rental business logic
- **AIService**: AI operations

**Location**: `domain/services.py`

**Benefits**:
- Reusable business logic
- Testable without HTTP layer
- Framework-agnostic

### 4. Configuration Pattern

Configuration is managed through environment variables:

1. **Environment Variables** (`.env`) - Runtime configuration loaded via Pydantic BaseSettings

**Location**: `core/settings.py`

**Settings**: All configuration values are loaded from `.env` file or environment variables

### 5. Factory Pattern

Infrastructure components use factory functions:

- **create_kernel()**: Semantic Kernel factory
- **get_async_session()**: Database session factory

**Location**: `core/ai_kernel.py`, `core/db.py`

## Component Relationships

### Request Flow

```
HTTP Request
    │
    ▼
api/v1/*_routes.py (Route Handler)
    │
    ▼ (Dependency Injection)
domain/services.py (Business Logic)
    │
    ▼ (Dependency Injection)
domain/repositories.py (Data Access)
    │
    ▼
core/db.py (Database Session)
    │
    ▼
PostgreSQL Database
```

### Dependency Graph

```
app/main.py
    ├── api/v1/router
    │   ├── film_routes → FilmService
    │   ├── rental_routes → RentalService
    │   ├── category_routes → CategoryService
    │   ├── customer_routes → CustomerService
    │   └── ai_routes → HandoffOrchestration
    │       └── create_handoff_orchestration()
    │           ├── SearchAgent (ChatCompletionAgent)
    │           │   └── FilmSearchPlugin (native function)
    │           └── LLMAgent (ChatCompletionAgent)
    │               └── llm_agent plugin (prompt-based)
    │
    └── core/
        ├── settings.py (used by all)
        ├── db.py (used by repositories)
        ├── dependencies.py (injection functions)
        ├── ai_kernel.py (used by agents)
        ├── plugin_loader.py (plugin registration)
        ├── auth.py (optional, for protected routes)
        └── logging.py (used by all)
```

## Data Flow

### Create Film Example

1. **HTTP Request** → `POST /api/v1/films/`
2. **Route Handler** → `film_routes.create_film()`
3. **Dependency Injection** → `FilmService` injected
4. **Service** → `FilmService.create_film()`
5. **Dependency Injection** → `FilmRepository` injected
6. **Repository** → `FilmRepository.create()`
7. **Database** → SQLModel insert operation
8. **Response** → FilmRead model returned

## Testing Patterns

### Test Structure

- **conftest.py**: Shared fixtures (database session, test client)
- **test_*.py**: Feature-specific tests

### Test Database

- Uses in-memory SQLite for tests
- Each test gets a fresh database session
- Dependency overrides for test isolation

**Location**: `tests/conftest.py`

## Migration Pattern

### Alembic Workflow

1. **Model Changes** → Update `domain/models.py`
2. **Generate Migration** → `alembic revision --autogenerate`
3. **Review Migration** → Check generated SQL
4. **Apply Migration** → `alembic upgrade head`

**Location**: `migrations/env.py`

## Logging Pattern

### Structured Logging

- Uses `structlog` for JSON logging
- Context variables for request tracking
- Log level from environment

**Location**: `core/logging.py`

## Authentication Pattern

### Bearer Token

- JWT-based authentication
- Token validation via dependency
- Optional protection on routes

**Location**: `core/auth.py`

**Usage**:
```python
@router.get("/protected")
async def protected_route(
    current_user: dict = Depends(get_current_user)
):
    return {"user": current_user}
```

## Agent Orchestration Pattern

### Semantic Kernel HandoffOrchestration

The project uses Semantic Kernel's native `HandoffOrchestration` to route questions between specialized agents:

- **SearchAgent**: Handles film-related questions using native function plugins
- **LLMAgent**: Handles general questions using prompt-based plugins
- **HandoffOrchestration**: Manages agent-to-agent transfers

**Location**: `app/agents/orchestration.py`

**Key Components**:
1. **ChatCompletionAgent**: Both agents use Semantic Kernel's `ChatCompletionAgent`
2. **OrchestrationHandoffs**: Defines handoff rules between agents
3. **InProcessRuntime**: Executes agents in API context
4. **Native Function Plugins**: Database operations exposed as kernel functions
5. **Prompt-based Plugins**: LLM operations using Semantic Kernel prompts

**Agent Creation**:
```python
def create_handoff_orchestration(session: AsyncSession, kernel: Kernel):
    # Create agents
    search_agent = SearchAgent(repository, kernel).agent
    llm_agent = LLMAgent(kernel).agent
    
    # Configure handoffs
    handoffs = (
        OrchestrationHandoffs()
        .add(
            source_agent=search_agent.name,
            target_agent=llm_agent.name,
            description="Transfer to LLMAgent if no film found"
        )
    )
    
    # Create orchestration
    orchestration = HandoffOrchestration(
        members=[search_agent, llm_agent],
        handoffs=handoffs
    )
    return orchestration
```

**Usage in API**:
```python
@router.post("/handoff")
async def handoff_question(request: HandoffRequest, service: HandoffService = Depends(get_handoff_service)):
    result = await service.process_question(request.question)
    return HandoffResponse(agent=result["agent"], answer=result["answer"])
```

**Service Layer Implementation**:
```python
class HandoffService:
    async def process_question(self, question: str) -> Dict[str, Any]:
        orchestration, agent_tracker = create_handoff_orchestration(self.session, self.kernel)
    runtime = InProcessRuntime()
    runtime.start()
        
        try:
            orchestration_result = await asyncio.wait_for(
                orchestration.invoke(task=question, runtime=runtime),
                timeout=30.0
            )
            # Extract response from tracker or orchestration result
            return {"agent": agent_name, "answer": answer}
        finally:
            runtime.stop()
```

## Plugin Pattern

### Native Function Plugins

Python functions exposed as Semantic Kernel tools:

**Location**: `plugins/film_search/film_search_plugin.py`

**Example**:
```python
from semantic_kernel.functions import kernel_function

class FilmSearchPlugin:
    @kernel_function(
        name="search_film",
        description="Search for a film by title"
    )
    async def search_film(self, title: str) -> Optional[dict]:
        return await self.repository.search_by_title_with_category(title)
```

**Registration**:
```python
plugin = FilmSearchPlugin(repository)
kernel.add_plugin(plugin, "film_search")
```

### Prompt-based Plugins

Semantic Kernel prompts loaded from directory structure:

**Structure**:
```
plugins/
    plugin_name/
        function_name/
            skprompt.txt
            config.json
```

**Registration**:
```python
kernel.add_plugin(
    plugin_name="plugin_name",
    parent_directory="plugins",
    encoding="utf-8"
)
```

**Location**: `core/plugin_loader.py`

## Response Extraction Pattern

### Agent Response Tracking

The orchestration system uses a sophisticated callback system to track agent responses:

**Key Components**:
1. **Agent Tracker Dictionary**: Mutable state shared between callbacks
2. **Response Callback**: Captures agent responses and extracts content
3. **Human Response Function**: Manages conversation flow and termination
4. **Service Layer**: Orchestrates the entire process with timeout handling

**Location**: `app/agents/orchestration.py`, `domain/services/handoff_service.py`

**Pattern**:
```python
def create_handoff_orchestration(session, kernel):
    agent_tracker = {
        "last_agent": "SearchAgent",
        "response_received": False,
        "last_agent_response": None,
        "should_stop": False
    }
    
    def agent_response_callback(message: ChatMessageContent):
        # Extract content from various message formats
        content = extract_content(message)
        if content and not agent_tracker.get("last_agent_response"):
            agent_tracker["last_agent_response"] = content
            agent_tracker["response_received"] = True
    
    orchestration = HandoffOrchestration(
        members=[search_agent, llm_agent],
        handoffs=handoffs,
        agent_response_callback=agent_response_callback,
        human_response_function=human_response_function
    )
    
    return orchestration, agent_tracker
```

**Benefits**:
- Captures first valid response (prevents duplicate responses)
- Handles multiple message formats from Semantic Kernel
- Provides fallback mechanisms for response extraction
- Tracks conversation state for proper termination

