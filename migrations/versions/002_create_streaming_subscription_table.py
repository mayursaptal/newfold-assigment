"""Migration: Create streaming_subscription table.

This migration creates a new 'streaming_subscription' table to track customer
streaming subscriptions. The table includes subscription plan information,
start and end dates, and references the customer table via foreign key.

Revision ID: 002
Revises: 001
Create Date: 2024-11-09 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema.

    Creates the 'streaming_subscription' table with the following columns:
    - id: Primary key
    - customer_id: Foreign key to customer table
    - plan_name: Subscription plan name (max 100 characters)
    - start_date: Subscription start date (required)
    - end_date: Subscription end date (optional)

    Uses Alembic's op.create_table() helper function for table creation.
    """
    # Create table using Alembic's helper function op.create_table()
    # This demonstrates using Alembic's helper for table creation
    op.create_table(
        "streaming_subscription",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("plan_name", sa.String(length=100), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["customer.customer_id"], name="fk_streaming_subscription_customer"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_streaming_subscription"),
    )


def downgrade() -> None:
    """Downgrade database schema.

    Drops the 'streaming_subscription' table, reverting the database
    to its previous state before this migration was applied.
    """
    # Drop table using Alembic's helper function op.drop_table()
    op.drop_table("streaming_subscription")
