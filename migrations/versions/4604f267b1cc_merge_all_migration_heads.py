"""merge_all_migration_heads

Revision ID: 4604f267b1cc
Revises: add_country_codes, 20260208_add_linkedin_link, 86f3df760347, ad1a9bd9c5de, add_parent_consent
Create Date: 2026-03-26 01:56:16.311518

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4604f267b1cc'
down_revision = ('add_country_codes', '20260208_add_linkedin_link', '86f3df760347', 'ad1a9bd9c5de', 'add_parent_consent')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
