"""Database setup and session management.

This module provides async database engine and session management using
SQLAlchemy's async capabilities with SQLModel. It handles connection
pooling, session lifecycle, and database initialization.

Example:
    ```python
    from core.db import get_async_session
    
    async for session in get_async_session():
        # Use session for database operations
        pass
    ```
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from typing import AsyncGenerator
from core.settings import settings


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function to get async database session.
    
    This is an async generator that yields a database session and
    automatically handles commit/rollback on success/failure.
    
    Yields:
        AsyncSession: Database session instance
        
    Example:
        ```python
        async for session in get_async_session():
            # Database operations
            result = await session.execute(query)
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables.
    
    Creates all database tables defined in SQLModel metadata.
    This should be called once at application startup.
    
    Note:
        This uses SQLModel.metadata.create_all which creates all
        tables defined in the application's models.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections.
    
    Disposes of the database engine and closes all connection pools.
    This should be called at application shutdown.
    """
    await engine.dispose()

