"""add profile_completion_email_sent to user

Revision ID: add_profile_completion_email_sent
Revises: a7e30197cde2
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_profile_completion_email_sent'
down_revision = 'a7e30197cde2'
branch_labels = None
depends_on = None


def upgrade():
    # Add profile_completion_email_sent column to user table
    # Using batch mode for SQLite compatibility
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_completion_email_sent', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    # Remove profile_completion_email_sent column from user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('profile_completion_email_sent')
