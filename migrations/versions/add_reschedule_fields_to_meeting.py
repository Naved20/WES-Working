"""Add reschedule fields to meeting_requests table

Revision ID: add_reschedule_fields
Revises: ff0a3d9f29b7
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_reschedule_fields'
down_revision = 'ff0a3d9f29b7'
branch_labels = None
depends_on = None


def upgrade():
    # Add reschedule fields to meeting_requests table
    with op.batch_alter_table('meeting_requests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_rescheduled', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('reschedule_reason', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('original_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('original_time', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('rescheduled_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('rescheduled_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_rescheduled_by', 'signup_details', ['rescheduled_by_id'], ['id'])


def downgrade():
    with op.batch_alter_table('meeting_requests', schema=None) as batch_op:
        batch_op.drop_constraint('fk_rescheduled_by', type_='foreignkey')
        batch_op.drop_column('rescheduled_by_id')
        batch_op.drop_column('rescheduled_at')
        batch_op.drop_column('original_time')
        batch_op.drop_column('original_date')
        batch_op.drop_column('reschedule_reason')
        batch_op.drop_column('is_rescheduled')
