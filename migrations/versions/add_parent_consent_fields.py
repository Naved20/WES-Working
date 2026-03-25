"""Add parent consent fields to mentee profile

Revision ID: add_parent_consent
Revises: 
Create Date: 2026-03-26

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_parent_consent'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add parent consent columns to mentee_profile table
    op.add_column('mentee_profile', sa.Column('parent_email', sa.String(150), nullable=True))
    op.add_column('mentee_profile', sa.Column('parent_consent_status', sa.String(20), nullable=True, server_default='pending'))
    op.add_column('mentee_profile', sa.Column('parent_consent_token', sa.String(200), nullable=True))
    op.add_column('mentee_profile', sa.Column('parent_consent_date', sa.DateTime(), nullable=True))
    
    # Update existing records to have default status
    op.execute("UPDATE mentee_profile SET parent_consent_status = 'approved' WHERE parent_consent_status IS NULL")


def downgrade():
    # Remove parent consent columns
    op.drop_column('mentee_profile', 'parent_consent_date')
    op.drop_column('mentee_profile', 'parent_consent_token')
    op.drop_column('mentee_profile', 'parent_consent_status')
    op.drop_column('mentee_profile', 'parent_email')
