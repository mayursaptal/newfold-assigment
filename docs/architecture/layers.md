# Layered Architecture Details

This document provides detailed information about each layer in the Interview API architecture, including responsibilities, patterns, and implementation details.

## 🎯 Architecture Principles

### Dependency Rule
Dependencies point inward. Outer layers depend on inner layers, never the reverse.

```
Infrastructure → Domain ← Presentation
      ↓           ↑
   Core/App ──────┘
```

### Layer Responsibilities

| Layer | Responsibility | Dependencies |
|-------|---------------|--------------|
| **Presentation** | HTTP interface, validation | Domain |
| **Domain** | Business logic, entities | None (pure) |
| **Infrastructure** | External concerns | Domain |
| **Application** | Orchestration, startup | All layers |

## 📁 Presentation Layer (`api/`)

### Purpose
Handle HTTP requests and responses, providing a clean interface to the domain layer.

### Structure
```
api/
├── __init__.py
└── v1/
    ├── __init__.py
    ├── ai_routes.py        # AI agent endpoints
    ├── category_routes.py  # Category CRUD
    ├── customer_routes.py  # Customer management
    ├── film_routes.py      # Film operations
    └── rental_routes.py    # Rental management
```

### Key Patterns

#### 1. Route Organization
```python
# api/v1/film_routes.py
from fastapi import APIRouter, Depends
from domain.services.film_service import FilmService
from domain.schemas.film import FilmResponse, FilmCreate

router = APIRouter(prefix="/films", tags=["films"])

@router.get("/", response_model=list[FilmResponse])
async def get_films(
    service: FilmService = Depends(get_film_service)
) -> list[FilmResponse]:
    return await service.get_all_films()
```

#### 2. Dependency Injection
```python
# Routes receive services via dependency injection
async def get_films(
    skip: int = 0,
    limit: int = 100,
    service: FilmService = Depends(get_film_service)
):
    # Service handles business logic
    return await service.get_films(skip=skip, limit=limit)
```

#### 3. Request/Response Models
```python
# Input validation
class FilmCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1900, le=2030)

# Response serialization
class FilmResponse(BaseModel):
    film_id: int
    title: str
    description: Optional[str]
    release_year: Optional[int]
    
    class Config:
        from_attributes = True
```

### Responsibilities
- ✅ HTTP request/response handling
- ✅ Input validation (Pydantic schemas)
- ✅ Response serialization
- ✅ Error handling and status codes
- ✅ API documentation (OpenAPI)
- ❌ Business logic (delegated to domain)
- ❌ Data access (delegated to domain)

## 🏢 Domain Layer (`domain/`)

### Purpose
Contains the core business logic, entities, and rules. This layer is independent of external concerns.

### Structure
```
domain/
├── models/          # Entity definitions
├── repositories/    # Data access interfaces
├── services/        # Business logic
└── schemas/         # Request/response models
```

### 1. Models (`domain/models/`)

#### Entity Definition
```python
# domain/models/film.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Film(SQLModel, table=True):
    __tablename__ = "film"
    
    film_id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    release_year: Optional[int] = Field(default=None)
    
    # Relationships
    category: Optional["Category"] = Relationship(back_populates="films")
    rentals: List["Rental"] = Relationship(back_populates="film")
```

#### Key Features
- **SQLModel Integration**: Type-safe ORM with Pydantic validation
- **Relationships**: Defined database relationships
- **Validation**: Built-in field validation
- **Serialization**: Automatic JSON serialization

### 2. Repositories (`domain/repositories/`)

#### Repository Pattern
```python
# domain/repositories/film_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.film import Film

class FilmRepository(ABC):
    @abstractmethod
    async def get_by_id(self, film_id: int) -> Optional[Film]:
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Film]:
        pass
    
    @abstractmethod
    async def create(self, film: Film) -> Film:
        pass
    
    @abstractmethod
    async def update(self, film: Film) -> Film:
        pass
    
    @abstractmethod
    async def delete(self, film_id: int) -> bool:
        pass
    
    @abstractmethod
    async def search_by_title(self, title: str) -> List[Film]:
        pass
```

#### Implementation
```python
# domain/repositories/film_repository.py (continued)
class SQLFilmRepository(FilmRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, film_id: int) -> Optional[Film]:
        result = await self.session.get(Film, film_id)
        return result
    
    async def search_by_title(self, title: str) -> List[Film]:
        query = select(Film).where(Film.title.ilike(f"%{title}%"))
        result = await self.session.exec(query)
        return result.all()
```

### 3. Services (`domain/services/`)

#### Business Logic Layer
```python
# domain/services/film_service.py
from typing import List, Optional
from domain.models.film import Film
from domain.repositories.film_repository import FilmRepository
from domain.schemas.film import FilmCreate, FilmUpdate

class FilmService:
    def __init__(self, repository: FilmRepository):
        self.repository = repository
    
    async def get_film_by_id(self, film_id: int) -> Optional[Film]:
        return await self.repository.get_by_id(film_id)
    
    async def search_films(self, query: str) -> List[Film]:
        # Business logic: search across multiple fields
        title_results = await self.repository.search_by_title(query)
        # Could add description search, category search, etc.
        return title_results
    
    async def create_film(self, film_data: FilmCreate) -> Film:
        # Business validation
        if await self._title_exists(film_data.title):
            raise ValueError("Film with this title already exists")
        
        film = Film(**film_data.dict())
        return await self.repository.create(film)
    
    async def _title_exists(self, title: str) -> bool:
        # Private business logic method
        results = await self.repository.search_by_title(title)
        return len(results) > 0
```

#### AI Service Integration
```python
# domain/services/handoff_service.py
class HandoffService:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.orchestration = self._create_orchestration()
    
    async def process_question(self, question: str) -> str:
        # Business logic for AI agent orchestration
        chat_history = ChatHistory()
        chat_history.add_user_message(question)
        
        # Execute orchestration
        async for response in self.orchestration.invoke_stream(
            kernel=self.kernel,
            chat_history=chat_history
        ):
            if hasattr(response, 'content'):
                return response.content
        
        return "No response generated"
```

### 4. Schemas (`domain/schemas/`)

#### Request/Response Models
```python
# domain/schemas/film.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FilmBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1900, le=2030)

class FilmCreate(FilmBase):
    pass

class FilmUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1900, le=2030)

class FilmResponse(FilmBase):
    film_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### Domain Layer Responsibilities
- ✅ Business logic and rules
- ✅ Entity definitions and relationships
- ✅ Data access abstractions (repositories)
- ✅ Service orchestration
- ✅ Domain validation
- ❌ HTTP concerns (handled by presentation)
- ❌ Database implementation details (handled by infrastructure)
- ❌ External API calls (handled by infrastructure)

## 🔧 Infrastructure Layer (`core/`)

### Purpose
Handle external concerns like databases, AI services, and configuration.

### Structure
```
core/
├── __init__.py
├── ai_kernel.py      # Semantic Kernel setup
├── auth.py           # Authentication
├── db.py             # Database configuration
├── dependencies.py   # Dependency injection
├── logging.py        # Logging configuration
├── plugin_loader.py  # AI plugin management
└── settings.py       # Configuration management
```

### Key Components

#### 1. Database Configuration
```python
# core/db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.settings import get_settings

settings = get_settings()

# Async engine configuration
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

#### 2. AI Kernel Setup
```python
# core/ai_kernel.py
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from core.settings import get_settings

def create_kernel() -> Kernel:
    settings = get_settings()
    
    kernel = Kernel()
    
    # Add AI service
    kernel.add_service(
        OpenAIChatCompletion(
            ai_model_id=settings.openai_model,
            api_key=settings.openai_api_key,
        )
    )
    
    return kernel
```

#### 3. Dependency Injection
```python
# core/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from domain.repositories.film_repository import SQLFilmRepository
from domain.services.film_service import FilmService

async def get_film_repository(
    session: AsyncSession = Depends(get_session)
) -> SQLFilmRepository:
    return SQLFilmRepository(session)

async def get_film_service(
    repository: SQLFilmRepository = Depends(get_film_repository)
) -> FilmService:
    return FilmService(repository)
```

### Infrastructure Responsibilities
- ✅ Database connection and configuration
- ✅ External API integrations
- ✅ Authentication and security
- ✅ Logging and monitoring
- ✅ Configuration management
- ✅ AI service setup
- ❌ Business logic (delegated to domain)
- ❌ HTTP handling (delegated to presentation)

## 🚀 Application Layer (`app/`)

### Purpose
Application entry point, startup configuration, and high-level orchestration.

### Structure
```
app/
├── __init__.py
├── main.py          # FastAPI application
└── agents/          # AI agent implementations
    ├── __init__.py
    ├── llm_agent.py
    ├── orchestration.py
    └── search_agent.py
```

### FastAPI Application Setup
```python
# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.db import init_db
from core.logging import setup_logging
from api.v1 import film_routes, ai_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    await init_db()
    yield
    # Shutdown
    # Cleanup code here

app = FastAPI(
    title="Interview API",
    description="FastAPI with AI agent orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(film_routes.router, prefix="/api/v1")
app.include_router(ai_routes.router, prefix="/api/v1")
```

## 🔄 Layer Interaction Patterns

### 1. Request Flow
```
HTTP Request → API Route → Service → Repository → Database
```

### 2. Dependency Flow
```python
# Presentation depends on Domain
from domain.services.film_service import FilmService

# Domain defines interfaces, Infrastructure implements
class FilmRepository(ABC):  # Domain interface
    pass

class SQLFilmRepository(FilmRepository):  # Infrastructure implementation
    pass
```

### 3. Error Handling
```python
# Domain raises business exceptions
class FilmNotFoundError(Exception):
    pass

# Presentation handles HTTP status codes
@router.get("/films/{film_id}")
async def get_film(film_id: int, service: FilmService = Depends()):
    try:
        film = await service.get_film_by_id(film_id)
        return film
    except FilmNotFoundError:
        raise HTTPException(status_code=404, detail="Film not found")
```

## 🧪 Testing Strategy by Layer

### Presentation Layer Tests
```python
# Test API endpoints
async def test_get_films(client: AsyncClient):
    response = await client.get("/api/v1/films/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Domain Layer Tests
```python
# Test business logic in isolation
async def test_film_service_create():
    mock_repo = Mock(spec=FilmRepository)
    service = FilmService(mock_repo)
    
    film_data = FilmCreate(title="Test Film")
    await service.create_film(film_data)
    
    mock_repo.create.assert_called_once()
```

### Infrastructure Layer Tests
```python
# Test database operations
async def test_film_repository_get_by_id(session: AsyncSession):
    repo = SQLFilmRepository(session)
    film = await repo.get_by_id(1)
    assert film is not None
```

This layered architecture ensures maintainable, testable, and scalable code while providing clear separation of concerns and dependency management.
