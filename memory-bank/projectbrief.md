# Project Brief

## Overview

Interview API is a FastAPI-based application demonstrating modern Python web development practices with:
- FastAPI for async web framework
- SQLModel for type-safe ORM
- Semantic Kernel for AI integration
- TOML configuration management
- Alembic for database migrations
- PostgreSQL in Docker

## Goals

1. Provide a clean, maintainable codebase following best practices
2. Demonstrate layered architecture with dependency injection
3. Integrate AI capabilities via Semantic Kernel
4. Support database migrations with Alembic
5. Include comprehensive testing infrastructure

## Core Requirements

- FastAPI application with async support
- SQLModel for database operations
- Semantic Kernel integration for AI features
- TOML configuration with environment variable override
- Alembic migrations for database schema management
- PostgreSQL database in Docker
- Dependency injection throughout the application
- Structured logging
- Authentication support (Bearer tokens)
- Test suite with pytest

## Architecture Pattern

The project follows a **layered architecture** inspired by pagila_api:

- **Presentation Layer** (`api/`) - HTTP endpoints
- **Domain Layer** (`domain/`) - Business logic, models, repositories, services
- **Infrastructure Layer** (`core/`) - Shared utilities, database, AI, auth, logging
- **Application Layer** (`app/`) - FastAPI app initialization

## Success Criteria

- ✅ All dependencies properly configured
- ✅ Database migrations working
- ✅ API endpoints functional
- ✅ Dependency injection implemented
- ✅ Tests passing
- ✅ Docker setup working
- ✅ Documentation complete

