"""add_streaming_available_to_film

Revision ID: 001
Revises: 
Create Date: 2024-11-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add streaming_available Boolean column with default FALSE
    # PostgreSQL defaults are documented and applied at the database level
    op.add_column('film', sa.Column('streaming_available', sa.Boolean(), 
                                     server_default=sa.text('false'), 
                                     nullable=False))


def downgrade() -> None:
    # Remove the streaming_available column
    op.drop_column('film', 'streaming_available')

