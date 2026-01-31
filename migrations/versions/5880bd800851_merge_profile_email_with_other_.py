"""merge profile email with other migrations

Revision ID: 5880bd800851
Revises: chat_system_001, add_institution_mentee, add_profile_completion_email_sent
Create Date: 2026-01-31 21:03:16.549914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5880bd800851'
down_revision = ('chat_system_001', 'add_institution_mentee', 'add_profile_completion_email_sent')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
