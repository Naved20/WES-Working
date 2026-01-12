"""Add OAuth fields to signup_details table

Revision ID: add_oauth_fields
Revises: add_reschedule_fields
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_oauth_fields'
down_revision = 'add_reschedule_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Add OAuth fields to signup_details table
    with op.batch_alter_table('signup_details', schema=None) as batch_op:
        batch_op.alter_column('password', existing_type=sa.String(length=200), nullable=True)
        batch_op.alter_column('user_type', existing_type=sa.String(length=10), nullable=True)
        batch_op.add_column(sa.Column('google_id', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('oauth_provider', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('profile_picture_url', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('oauth_created_at', sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint('uq_google_id', ['google_id'])


def downgrade():
    with op.batch_alter_table('signup_details', schema=None) as batch_op:
        batch_op.drop_constraint('uq_google_id', type_='unique')
        batch_op.drop_column('oauth_created_at')
        batch_op.drop_column('profile_picture_url')
        batch_op.drop_column('oauth_provider')
        batch_op.drop_column('google_id')
        batch_op.alter_column('user_type', existing_type=sa.String(length=10), nullable=False)
        batch_op.alter_column('password', existing_type=sa.String(length=200), nullable=False)
