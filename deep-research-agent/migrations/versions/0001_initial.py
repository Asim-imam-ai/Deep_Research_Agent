"""Initial application tables.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
from research_assistant.infrastructure.database.models import Base
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Importing Base.metadata here ensures tables match the ORM definitions.
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

def downgrade():
    Base.metadata.drop_all(bind=op.get_bind())
