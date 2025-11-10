"""Migration: Add streaming_available column to film table.

This migration adds a Boolean column 'streaming_available' to the 'film' table
with a default value of FALSE. This allows tracking which films are available
for streaming services.

Revision ID: 001
Revises:
Create Date: 2024-11-09 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema.

    Adds the 'streaming_available' Boolean column to the 'film' table
    with a default value of FALSE. The default is applied at the database
    level using PostgreSQL's server_default.
    """
    # Add streaming_available Boolean column with default FALSE
    # PostgreSQL defaults are documented and applied at the database level
    op.add_column(
        "film",
        sa.Column(
            "streaming_available", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )


def downgrade() -> None:
    """Downgrade database schema.

    Removes the 'streaming_available' column from the 'film' table,
    reverting the database to its previous state.
    """
    # Remove the streaming_available column
    op.drop_column("film", "streaming_available")
