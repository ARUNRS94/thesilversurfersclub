"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    from app.models import Base
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

def downgrade():
    op.drop_table('audit_logs'); op.drop_table('notifications'); op.drop_table('notification_templates'); op.drop_table('group_posts'); op.drop_table('group_memberships'); op.drop_table('interest_groups'); op.drop_table('announcements'); op.drop_table('payments'); op.drop_table('documents'); op.drop_table('trip_registrations'); op.drop_table('trips'); op.drop_table('attendance'); op.drop_table('event_registrations'); op.drop_table('events'); op.drop_table('memberships'); op.drop_table('members'); op.drop_table('users'); op.drop_table('organizations')
