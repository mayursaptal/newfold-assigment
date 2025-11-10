# Database Architecture & Management

The Interview API uses PostgreSQL as its primary database with a comprehensive migration system, sample data, and optimized configuration for both development and production environments.

## 🗄️ Database Overview

### Technology Stack
- **Database**: PostgreSQL 15 (Alpine Linux container)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Driver**: asyncpg (async PostgreSQL driver)
- **Migrations**: Alembic
- **Sample Data**: Pagila (PostgreSQL sample database)

### Database Architecture
```
┌─────────────────────────────────────────┐
│              Application Layer           │
├─────────────────────────────────────────┤
│              SQLModel ORM               │
├─────────────────────────────────────────┤
│              asyncpg Driver             │
├─────────────────────────────────────────┤
│            PostgreSQL 15                │
└─────────────────────────────────────────┘
```

## 📊 Database Schema

### Core Entities

#### Film Entity
```sql
CREATE TABLE film (
    film_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_year INTEGER,
    language_id INTEGER,
    rental_duration INTEGER DEFAULT 3,
    rental_rate DECIMAL(4,2) DEFAULT 4.99,
    length INTEGER,
    replacement_cost DECIMAL(5,2) DEFAULT 19.99,
    rating VARCHAR(10) DEFAULT 'G',
    special_features TEXT[],
    last_update TIMESTAMP DEFAULT NOW(),
    streaming_available BOOLEAN DEFAULT FALSE
);
```

#### Category Entity
```sql
CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(25) NOT NULL,
    last_update TIMESTAMP DEFAULT NOW()
);
```

#### Rental Entity
```sql
CREATE TABLE rental (
    rental_id SERIAL PRIMARY KEY,
    rental_date TIMESTAMP NOT NULL,
    inventory_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    return_date TIMESTAMP,
    staff_id INTEGER NOT NULL,
    last_update TIMESTAMP DEFAULT NOW()
);
```

### Entity Relationships
```
Category ──┐
           │ 1:N (film_category)
           ▼
         Film ──┐
                │ 1:N (inventory)
                ▼
            Inventory ──┐
                        │ 1:N
                        ▼
                     Rental ──┐
                               │ N:1
                               ▼
                           Customer
```

## 🏗️ SQLModel Implementation

### Model Definitions
```python
# domain/models/film.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Film(SQLModel, table=True):
    __tablename__ = "film"
    
    film_id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None)
    release_year: Optional[int] = Field(default=None, index=True)
    language_id: Optional[int] = Field(default=None, foreign_key="language.language_id")
    rental_duration: int = Field(default=3)
    rental_rate: float = Field(default=4.99)
    length: Optional[int] = Field(default=None)
    replacement_cost: float = Field(default=19.99)
    rating: Optional[str] = Field(default="G", max_length=10)
    special_features: Optional[str] = Field(default=None)
    last_update: datetime = Field(default_factory=datetime.utcnow)
    streaming_available: bool = Field(default=False)
    
    # Relationships
    language: Optional["Language"] = Relationship(back_populates="films")
    film_categories: List["FilmCategory"] = Relationship(back_populates="film")
    inventory: List["Inventory"] = Relationship(back_populates="film")

class Category(SQLModel, table=True):
    __tablename__ = "category"
    
    category_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=25, unique=True, index=True)
    last_update: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    film_categories: List["FilmCategory"] = Relationship(back_populates="category")

class FilmCategory(SQLModel, table=True):
    __tablename__ = "film_category"
    
    film_id: int = Field(foreign_key="film.film_id", primary_key=True)
    category_id: int = Field(foreign_key="category.category_id", primary_key=True)
    last_update: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    film: Film = Relationship(back_populates="film_categories")
    category: Category = Relationship(back_populates="film_categories")
```

### Repository Pattern
```python
# domain/repositories/film_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models.film import Film

class FilmRepository(ABC):
    @abstractmethod
    async def get_by_id(self, film_id: int) -> Optional[Film]:
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Film]:
        pass
    
    @abstractmethod
    async def search_by_title(self, title: str) -> List[Film]:
        pass
    
    @abstractmethod
    async def get_by_category(self, category_name: str) -> List[Film]:
        pass

class SQLFilmRepository(FilmRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, film_id: int) -> Optional[Film]:
        return await self.session.get(Film, film_id)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Film]:
        query = select(Film).offset(skip).limit(limit)
        result = await self.session.exec(query)
        return result.all()
    
    async def search_by_title(self, title: str) -> List[Film]:
        query = select(Film).where(Film.title.ilike(f"%{title}%"))
        result = await self.session.exec(query)
        return result.all()
    
    async def get_by_category(self, category_name: str) -> List[Film]:
        query = (
            select(Film)
            .join(FilmCategory)
            .join(Category)
            .where(Category.name.ilike(f"%{category_name}%"))
        )
        result = await self.session.exec(query)
        return result.all()
```

## 🔧 Database Configuration

### Connection Setup
```python
# core/db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from core.settings import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "server_settings": {
            "application_name": "interview_api",
        }
    }
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_session() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
```

### Environment Configuration
```python
# core/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/interview_db"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "interview_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Connection pool settings
    db_pool_size: int = 20
    db_max_overflow: int = 0
    db_pool_recycle: int = 3600
    
    class Config:
        env_file = ".env"
```

## 🔄 Migration Management

### Alembic Configuration
```python
# migrations/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel
import asyncio
from core.db import engine
from domain.models import *  # Import all models

# Alembic Config object
config = context.config

# Set SQLModel metadata
target_metadata = SQLModel.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

### Migration Commands
```bash
# Create new migration
alembic revision --autogenerate -m "Add streaming_available to film"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history

# Show SQL for migration (dry run)
alembic upgrade head --sql
```

### Migration Example
```python
# migrations/versions/001_add_streaming_available_to_film.py
"""Add streaming_available to film

Revision ID: 001
Revises: 
Create Date: 2024-11-09 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add streaming_available column to film table."""
    op.add_column('film', sa.Column('streaming_available', sa.Boolean(), nullable=False, server_default='false'))

def downgrade() -> None:
    """Remove streaming_available column from film table."""
    op.drop_column('film', 'streaming_available')
```

## 📊 Sample Data (Pagila Database)

### Pagila Overview
The project uses the Pagila sample database, which is a PostgreSQL port of the MySQL Sakila database.

**Entities Included**:
- Films (1000+ movies)
- Categories (16 genres)
- Actors (200+ actors)
- Customers (599 customers)
- Rentals (16,000+ rental records)
- Stores, Staff, Addresses, Cities, Countries

### Data Loading Process
```sql
-- Schema creation (01-pagila-schema.sql)
CREATE TABLE film (
    film_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    -- ... other columns
);

-- Data insertion (02-pagila-data.sql)
INSERT INTO film (title, description, release_year, ...) VALUES
('ACADEMY DINOSAUR', 'A Epic Drama of a Feminist...', 2006, ...),
('ACE GOLDFINGER', 'A Astounding Epistle of a Database...', 2006, ...),
-- ... thousands more records
```

### Automatic Data Restoration
```yaml
# docker-compose.yml
postgres:
  image: postgres:15-alpine
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ../sql:/docker-entrypoint-initdb.d:ro  # Auto-load SQL files
```

### Manual Data Restoration
```bash
# Using psql directly
psql -h localhost -U postgres -d interview_db -f sql/01-pagila-schema.sql
psql -h localhost -U postgres -d interview_db -f sql/02-pagila-data.sql

# Using Python script
python scripts/restore_pagila.py

# Using container exec
docker exec -i interview_postgres psql -U postgres -d interview_db < sql/01-pagila-schema.sql
```

## 🔍 Query Optimization

### Indexing Strategy
```sql
-- Primary indexes (automatically created)
CREATE INDEX idx_film_title ON film(title);
CREATE INDEX idx_film_release_year ON film(release_year);
CREATE INDEX idx_rental_date ON rental(rental_date);

-- Composite indexes for common queries
CREATE INDEX idx_film_category_lookup ON film_category(category_id, film_id);
CREATE INDEX idx_rental_customer_date ON rental(customer_id, rental_date);

-- Full-text search indexes
CREATE INDEX idx_film_title_fulltext ON film USING gin(to_tsvector('english', title));
CREATE INDEX idx_film_description_fulltext ON film USING gin(to_tsvector('english', description));
```

### Query Performance
```python
# Optimized repository methods
class SQLFilmRepository(FilmRepository):
    async def search_films_optimized(self, query: str, limit: int = 10) -> List[Film]:
        """Optimized film search with proper indexing."""
        # Use ILIKE with index-friendly patterns
        search_query = select(Film).where(
            Film.title.ilike(f"{query}%")  # Prefix search uses index
        ).limit(limit)
        
        result = await self.session.exec(search_query)
        return result.all()
    
    async def get_films_by_category_optimized(self, category_id: int) -> List[Film]:
        """Optimized category-based film retrieval."""
        query = (
            select(Film)
            .join(FilmCategory, Film.film_id == FilmCategory.film_id)
            .where(FilmCategory.category_id == category_id)
            .options(selectinload(Film.film_categories))  # Eager loading
        )
        
        result = await self.session.exec(query)
        return result.all()
```

## 🧪 Testing Database Setup

### Test Database Configuration
```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlalchemy.pool import StaticPool

# In-memory SQLite for fast tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
```

### Test Data Factories
```python
# tests/factories.py
from domain.models.film import Film, Category
from datetime import datetime

class FilmFactory:
    @staticmethod
    def create_film(**kwargs) -> Film:
        defaults = {
            "title": "Test Film",
            "description": "A test film description",
            "release_year": 2023,
            "rental_duration": 3,
            "rental_rate": 4.99,
            "replacement_cost": 19.99,
            "rating": "PG",
            "last_update": datetime.utcnow(),
            "streaming_available": False
        }
        defaults.update(kwargs)
        return Film(**defaults)

class CategoryFactory:
    @staticmethod
    def create_category(**kwargs) -> Category:
        defaults = {
            "name": "Test Category",
            "last_update": datetime.utcnow()
        }
        defaults.update(kwargs)
        return Category(**defaults)
```

## 📊 Database Monitoring

### Health Checks
```python
# Health check endpoint
@app.get("/health/db")
async def database_health(session: AsyncSession = Depends(get_session)):
    try:
        # Simple query to test database connectivity
        result = await session.exec(select(1))
        result.first()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }
```

### Performance Metrics
```python
# Query performance logging
import time
from functools import wraps

def log_query_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.info(
            "Database query executed",
            function=func.__name__,
            execution_time=execution_time,
            args_count=len(args),
            kwargs_count=len(kwargs)
        )
        
        return result
    return wrapper
```

## 🔒 Security Considerations

### Connection Security
```python
# Secure connection configuration
engine = create_async_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",  # Require SSL in production
        "server_settings": {
            "application_name": "interview_api",
        }
    }
)
```

### SQL Injection Prevention
```python
# Safe parameterized queries (SQLModel handles this automatically)
async def search_films_safe(self, title: str) -> List[Film]:
    # SQLModel automatically parameterizes queries
    query = select(Film).where(Film.title.ilike(f"%{title}%"))
    result = await self.session.exec(query)
    return result.all()

# Never do this (vulnerable to SQL injection)
# query = f"SELECT * FROM film WHERE title LIKE '%{title}%'"
```

### Database Permissions
```sql
-- Create application user with limited permissions
CREATE USER interview_app WITH PASSWORD 'secure_password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE interview_db TO interview_app;
GRANT USAGE ON SCHEMA public TO interview_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO interview_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO interview_app;
```

This database architecture provides a robust, scalable, and maintainable foundation for the Interview API with proper separation of concerns, performance optimization, and comprehensive testing support.
