#!/bin/bash
# Script to restore Pagila database from SQL files using psql

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SQL_DIR="$PROJECT_DIR/sql"

# Database connection parameters (from .env or defaults)
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-interview_db}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_PASSWORD="${POSTGRES_PASSWORD:-postgres}"

echo -e "${YELLOW}Starting Pagila database restoration...${NC}"

# Check if SQL files exist (try both old and new naming)
SCHEMA_FILE=""
DATA_FILE=""

if [ -f "$SQL_DIR/01-pagila-schema.sql" ]; then
    SCHEMA_FILE="$SQL_DIR/01-pagila-schema.sql"
elif [ -f "$SQL_DIR/pagila-schema.sql" ]; then
    SCHEMA_FILE="$SQL_DIR/pagila-schema.sql"
else
    echo -e "${RED}Error: Schema file not found in $SQL_DIR${NC}"
    exit 1
fi

if [ -f "$SQL_DIR/02-pagila-data.sql" ]; then
    DATA_FILE="$SQL_DIR/02-pagila-data.sql"
elif [ -f "$SQL_DIR/pagila-data.sql" ]; then
    DATA_FILE="$SQL_DIR/pagila-data.sql"
else
    echo -e "${RED}Error: Data file not found in $SQL_DIR${NC}"
    exit 1
fi

# Set PGPASSWORD environment variable
export PGPASSWORD="$DB_PASSWORD"

echo -e "${YELLOW}Restoring schema...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCHEMA_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Schema restored successfully${NC}"
else
    echo -e "${RED}Error restoring schema${NC}"
    exit 1
fi

echo -e "${YELLOW}Restoring data...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$DATA_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Data restored successfully${NC}"
else
    echo -e "${RED}Error restoring data${NC}"
    exit 1
fi

# Verify restoration
echo -e "${YELLOW}Verifying restoration...${NC}"
FILM_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM film;")
echo -e "${GREEN}Restoration complete! Film count: $FILM_COUNT${NC}"

# Unset PGPASSWORD
unset PGPASSWORD

echo -e "${GREEN}Pagila database restoration completed successfully!${NC}"

