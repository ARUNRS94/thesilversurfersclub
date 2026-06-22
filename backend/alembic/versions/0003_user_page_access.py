"""add user page access

Revision ID: 0003_user_page_access
Revises: 0002_membership_types
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = '0003_user_page_access'
down_revision = '0002_membership_types'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('allowed_pages', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('users', 'allowed_pages')
