"""Script to restore Pagila database from SQL files.

This script manually restores the Pagila sample database by executing
SQL schema and data files. It can be used as an alternative to the
automatic restoration via Docker volume mounts.

Usage:
    ```bash
    python scripts/restore_pagila.py
    ```

Note:
    The script expects SQL files in the sql/ directory:
    - 01-pagila-schema.sql (or pagila-schema.sql)
    - 02-pagila-data.sql (or pagila-data.sql)
"""

import asyncio
import asyncpg
from pathlib import Path
from core.settings import settings
from core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def restore_database():
    """Restore Pagila database from SQL files.
    
    Connects to PostgreSQL and executes schema and data SQL files
    in the correct order. Handles both old and new file naming conventions.
    
    Raises:
        FileNotFoundError: If SQL files are not found
        Exception: If database connection or execution fails
    """
    # Get SQL file paths (try both old and new naming)
    sql_dir = Path(__file__).parent.parent / "sql"
    
    # Try new naming first, fall back to old naming
    schema_file = sql_dir / "01-pagila-schema.sql"
    if not schema_file.exists():
        schema_file = sql_dir / "pagila-schema.sql"
    
    data_file = sql_dir / "02-pagila-data.sql"
    if not data_file.exists():
        data_file = sql_dir / "pagila-data.sql"
    
    if not schema_file.exists():
        logger.error(f"Schema file not found in {sql_dir}")
        return
    
    if not data_file.exists():
        logger.error(f"Data file not found in {sql_dir}")
        return
    
    # Parse database URL to get connection parameters
    # Format: postgresql+asyncpg://user:password@host:port/dbname
    db_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    logger.info("Starting Pagila database restoration", database_url=db_url)
    
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(db_url)
        logger.info("Connected to database")
        
        # Read and execute schema file
        logger.info("Loading schema file", file=str(schema_file))
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        
        # Execute schema in a transaction
        async with conn.transaction():
            # Split by semicolon and execute statements
            statements = [s.strip() for s in schema_sql.split(';') if s.strip() and not s.strip().startswith('--')]
            for i, statement in enumerate(statements):
                if statement:
                    try:
                        await conn.execute(statement)
                    except Exception as e:
                        # Some statements might fail (like CREATE SCHEMA if it exists)
                        logger.warning(f"Statement {i} failed (may be expected): {str(e)[:100]}")
        
        logger.info("Schema restored successfully")
        
        # Read and execute data file
        logger.info("Loading data file", file=str(data_file))
        with open(data_file, "r", encoding="utf-8") as f:
            data_sql = f.read()
        
        # Execute data in a transaction
        async with conn.transaction():
            # For COPY statements, we need to handle them differently
            # Split by newlines for COPY statements
            statements = [s.strip() for s in data_sql.split('\n') if s.strip() and not s.strip().startswith('--')]
            current_statement = []
            for line in statements:
                if line.startswith('COPY') or line.startswith('\\\.') or current_statement:
                    current_statement.append(line)
                    if line == '\\\.':
                        # End of COPY statement
                        full_statement = '\n'.join(current_statement)
                        await conn.execute(full_statement)
                        current_statement = []
                elif line and not line.startswith('--'):
                    # Regular SQL statement
                    if line.endswith(';'):
                        await conn.execute(line)
                    else:
                        current_statement.append(line)
        
        logger.info("Data restored successfully")
        
        # Verify restoration
        count = await conn.fetchval("SELECT COUNT(*) FROM film")
        logger.info("Restoration complete", film_count=count)
        
        await conn.close()
        logger.info("Database connection closed")
        
    except Exception as e:
        logger.error("Error restoring database", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(restore_database())

