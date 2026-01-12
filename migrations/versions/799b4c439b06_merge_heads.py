"""merge_heads

Revision ID: 799b4c439b06
Revises: add_oauth_fields, efaca4f8de5c
Create Date: 2026-01-12 11:44:49.048068

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '799b4c439b06'
down_revision = ('add_oauth_fields', 'efaca4f8de5c')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
