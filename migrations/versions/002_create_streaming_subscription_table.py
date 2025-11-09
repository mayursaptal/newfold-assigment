"""create_streaming_subscription_table

Revision ID: 002
Revises: 001
Create Date: 2024-11-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create table using Alembic's helper function op.create_table()
    # This demonstrates using Alembic's helper for table creation
    op.create_table(
        'streaming_subscription',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('plan_name', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customer.customer_id'], name='fk_streaming_subscription_customer'),
        sa.PrimaryKeyConstraint('id', name='pk_streaming_subscription')
    )


def downgrade() -> None:
    # Drop table using Alembic's helper function op.drop_table()
    op.drop_table('streaming_subscription')

