# Alembic Migrations

This directory contains database migration scripts managed by Alembic.

## Migration Files

### Migration #1: `001_add_streaming_available_to_film.py`
- **Purpose**: Adds a Boolean column `streaming_available` to the `film` table
- **PostgreSQL Default**: Uses `server_default=sa.text('false')` which is documented in PostgreSQL
- **Key Feature**: Demonstrates adding a Boolean column with a default value (FALSE) at the database level

### Migration #2: `002_create_streaming_subscription_table.py`
- **Purpose**: Creates `streaming_subscription` table using Alembic's helper functions
- **Alembic Helpers Used**: 
  - `op.create_table()` - Creates table with columns, constraints, and foreign keys
  - `op.drop_table()` - Drops table
- **Table Created**: `streaming_subscription`
  - Columns: 
    - `id` - Primary key (Integer)
    - `customer_id` - Foreign key to `customer` table
    - `plan_name` - String(100)
    - `start_date` - DateTime
    - `end_date` - DateTime (nullable)
  - Foreign key to `customer` table

## Autogenerate Configuration

The `env.py` file is configured with:
- `compare_type=True` - Compares column types between SQLModel metadata and DB schema
- `compare_server_default=True` - Compares server defaults

This allows Alembic to detect differences when using `--autogenerate`.

## Usage

### Create a new migration (autogenerate)
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback one migration
```bash
alembic downgrade -1
```

### Show current revision
```bash
alembic current
```

### Compare SQLModel metadata with DB schema
```bash
alembic revision --autogenerate -m "sync_with_models"
```

## Notes

- Migrations are ordered by revision ID (001, 002, etc.)
- Each migration has `upgrade()` and `downgrade()` functions
- The `down_revision` links migrations in a chain
- Autogenerate compares SQLModel metadata (`target_metadata`) with the actual database schema

