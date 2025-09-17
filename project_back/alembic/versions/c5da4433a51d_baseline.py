"""baseline

Revision ID: c5da4433a51d
Revises: 
Create Date: 2025-09-17 10:03:31.716144

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c5da4433a51d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 基线占位：不改动现有数据库
    pass


def downgrade() -> None:
    # 无需回滚
    pass
