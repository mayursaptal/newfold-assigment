# System Architecture Overview

The Interview API follows a **layered architecture** pattern inspired by Domain-Driven Design (DDD) and Clean Architecture principles, providing clear separation of concerns and maintainable code structure.

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   API Routes    │  │   Validation    │  │  Serialization  │  │
│  │   (FastAPI)     │  │   (Pydantic)    │  │   (Schemas)     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Domain Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │    Services     │  │   Repositories  │  │     Models      │  │
│  │ (Business Logic)│  │ (Data Access)   │  │   (Entities)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Infrastructure Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │    Database     │  │   AI Services   │  │   External      │  │
│  │  (PostgreSQL)   │  │ (Semantic Kernel│  │     APIs        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Layer Structure

### 1. Presentation Layer (`api/`)
**Responsibility**: HTTP interface and request/response handling

- **API Routes** (`api/v1/`): REST endpoints organized by domain
- **Request Validation**: Automatic validation using Pydantic schemas
- **Response Serialization**: Consistent JSON responses
- **Error Handling**: Centralized exception handling

**Key Files**:
- `api/v1/film_routes.py` - Film-related endpoints
- `api/v1/ai_routes.py` - AI agent endpoints
- `api/v1/rental_routes.py` - Rental management
- `api/v1/category_routes.py` - Category operations

### 2. Domain Layer (`domain/`)
**Responsibility**: Business logic and core entities

#### Models (`domain/models/`)
- **Entities**: Core business objects (Film, Category, Rental)
- **SQLModel Integration**: Type-safe ORM with Pydantic validation
- **Relationships**: Defined database relationships

#### Services (`domain/services/`)
- **Business Logic**: Core application operations
- **Orchestration**: Coordination between repositories
- **Validation**: Business rule enforcement
- **AI Integration**: Agent orchestration and handoff logic

#### Repositories (`domain/repositories/`)
- **Data Access**: Abstract database operations
- **Query Logic**: Complex database queries
- **Async Operations**: Non-blocking database access

#### Schemas (`domain/schemas/`)
- **Request/Response Models**: API contract definitions
- **Validation Rules**: Input validation and serialization
- **Type Safety**: Compile-time type checking

### 3. Infrastructure Layer (`core/`)
**Responsibility**: External concerns and technical implementation

- **Database Configuration** (`core/db.py`): Connection management
- **AI Kernel** (`core/ai_kernel.py`): Semantic Kernel setup
- **Authentication** (`core/auth.py`): Security implementation
- **Logging** (`core/logging.py`): Structured logging
- **Settings** (`core/settings.py`): Configuration management
- **Dependencies** (`core/dependencies.py`): Dependency injection

### 4. Application Layer (`app/`)
**Responsibility**: Application entry point and orchestration

- **FastAPI App** (`app/main.py`): Application initialization
- **AI Agents** (`app/agents/`): Intelligent agent implementations
- **Middleware**: Cross-cutting concerns
- **Startup/Shutdown**: Application lifecycle management

## 🔄 Data Flow

### 1. Request Processing Flow
```
HTTP Request → API Route → Schema Validation → Service Layer → Repository → Database
                    ↓
HTTP Response ← Response Schema ← Business Logic ← Data Access ← Query Result
```

### 2. AI Agent Flow
```
User Question → AI Route → Handoff Service → Agent Orchestration → Specialized Agent
                    ↓
Response ← Response Processing ← Agent Response ← Plugin Execution ← AI/Database
```

## 🎯 Design Principles

### 1. Separation of Concerns
- Each layer has a single, well-defined responsibility
- Dependencies flow inward (Dependency Inversion)
- Business logic is isolated from infrastructure

### 2. Dependency Injection
- Services are injected rather than instantiated
- Facilitates testing and modularity
- Configured in `core/dependencies.py`

### 3. Interface Segregation
- Small, focused interfaces
- Repository pattern abstracts data access
- Service interfaces define business operations

### 4. Single Responsibility
- Each class/module has one reason to change
- Clear boundaries between concerns
- Focused, cohesive components

## 🔌 Plugin Architecture

The application uses Semantic Kernel's plugin system for AI capabilities:

### Native Function Plugins
```python
@kernel_function(name="search_films", description="Search for films")
async def search_films(self, query: str) -> dict:
    # Database integration
    pass
```

### Prompt-Based Plugins
```
plugins/
├── llm_agent/
│   └── answer_question/
│       ├── skprompt.txt
│       └── config.json
└── film_summary/
    └── summarize_tool/
        ├── skprompt.txt
        └── config.json
```

## 🔄 Agent Orchestration

### HandoffOrchestration Pattern
```python
# Agent creation and configuration
search_agent = ChatCompletionAgent(...)
llm_agent = ChatCompletionAgent(...)

# Orchestration setup
orchestration = HandoffOrchestration(agents=[search_agent, llm_agent])
```

### Agent Specialization
- **SearchAgent**: Film database queries and movie-related questions
- **LLMAgent**: General knowledge and conversation handling
- **Intelligent Routing**: Automatic agent selection based on question context

## 📊 Database Architecture

### Entity Relationships
```
Category ──┐
           │ 1:N
           ▼
         Film ──┐
                │ 1:N
                ▼
             Rental
```

### Migration Strategy
- **Alembic Integration**: Version-controlled schema changes
- **Automatic Detection**: Schema change detection
- **Rollback Support**: Safe deployment and rollback

## 🛡️ Security Architecture

### Authentication Flow
```
Request → Bearer Token → JWT Validation → User Context → Authorization
```

### Security Layers
- **JWT Authentication**: Stateless token-based auth
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLModel parameterized queries
- **CORS Configuration**: Cross-origin request handling

## 🔍 Observability

### Logging Strategy
- **Structured Logging**: JSON format for production
- **Contextual Information**: Request IDs and user context
- **Multiple Levels**: Debug, Info, Warning, Error
- **Async Logging**: Non-blocking log operations

### Health Monitoring
- **Health Endpoints**: System status checking
- **Database Health**: Connection and query validation
- **AI Service Health**: Semantic Kernel status

## 🚀 Scalability Considerations

### Horizontal Scaling
- **Stateless Design**: No server-side session state
- **Database Connection Pooling**: Efficient resource usage
- **Async Operations**: High concurrency support

### Performance Optimization
- **Lazy Loading**: On-demand resource loading
- **Connection Pooling**: Database connection reuse
- **Caching Strategy**: Ready for Redis integration
- **Async/Await**: Non-blocking I/O operations

## 🧪 Testing Architecture

### Test Pyramid
```
    ┌─────────────┐
    │   E2E Tests │  ← Few, high-value integration tests
    └─────────────┘
  ┌─────────────────┐
  │ Integration Tests│  ← API and database integration
  └─────────────────┘
┌─────────────────────┐
│    Unit Tests       │  ← Many, fast, isolated tests
└─────────────────────┘
```

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Database Tests**: Repository and service testing
- **AI Tests**: Mocked AI service testing

This architecture provides a solid foundation for maintainable, scalable, and testable code while supporting modern development practices and AI integration.
