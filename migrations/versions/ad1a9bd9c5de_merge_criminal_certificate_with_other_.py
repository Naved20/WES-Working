"""merge criminal certificate with other migrations

Revision ID: ad1a9bd9c5de
Revises: 5880bd800851, add_criminal_certificate
Create Date: 2026-02-01 13:07:13.560412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad1a9bd9c5de'
down_revision = ('5880bd800851', 'add_criminal_certificate')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
