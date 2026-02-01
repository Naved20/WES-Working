"""add criminal certificate field to mentor profile

Revision ID: add_criminal_certificate
Revises: 
Create Date: 2026-02-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_criminal_certificate'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add criminal_certificate column to mentor_profile table
    op.add_column('mentor_profile', sa.Column('criminal_certificate', sa.String(length=100), nullable=True))


def downgrade():
    # Remove criminal_certificate column from mentor_profile table
    op.drop_column('mentor_profile', 'criminal_certificate')
