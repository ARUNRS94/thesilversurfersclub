"""add membership types master

Revision ID: 0002_membership_types
Revises: 0001_initial
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = '0002_membership_types'
down_revision = '0001_initial'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'membership_types',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=80), nullable=False, unique=True),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('fee', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

def downgrade():
    op.drop_table('membership_types')
