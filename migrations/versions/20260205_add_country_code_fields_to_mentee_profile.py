"""Add country code fields to mentee profile

Revision ID: add_country_codes
Revises: 
Create Date: 2026-02-05 21:45:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_country_codes'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add country code columns to mentee_profile table
    op.add_column('mentee_profile', sa.Column('mobile_country_code', sa.String(10), nullable=True, default='+91'))
    op.add_column('mentee_profile', sa.Column('whatsapp_country_code', sa.String(10), nullable=True, default='+91'))
    op.add_column('mentee_profile', sa.Column('parent_mobile_country_code', sa.String(10), nullable=True, default='+91'))
    
    # Update existing records to have default country code
    op.execute("UPDATE mentee_profile SET mobile_country_code = '+91' WHERE mobile_country_code IS NULL")
    op.execute("UPDATE mentee_profile SET whatsapp_country_code = '+91' WHERE whatsapp_country_code IS NULL")
    op.execute("UPDATE mentee_profile SET parent_mobile_country_code = '+91' WHERE parent_mobile_country_code IS NULL")

def downgrade():
    # Remove country code columns
    op.drop_column('mentee_profile', 'parent_mobile_country_code')
    op.drop_column('mentee_profile', 'whatsapp_country_code')
    op.drop_column('mentee_profile', 'mobile_country_code')