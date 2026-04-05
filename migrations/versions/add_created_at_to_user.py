"""add created_at to user

Revision ID: add_created_at_user
Revises: 4604f267b1cc
Create Date: 2026-04-05

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_created_at_user'
down_revision = '4604f267b1cc'
branch_labels = None
depends_on = None


def upgrade():
    # Add created_at column with default value
    op.add_column('signup_details', 
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )
    
    # Update existing records to set created_at to current time
    # This is a one-time operation for existing users
    op.execute(
        "UPDATE signup_details SET created_at = datetime('now') WHERE created_at IS NULL"
    )


def downgrade():
    op.drop_column('signup_details', 'created_at')
