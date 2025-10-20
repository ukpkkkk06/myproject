"""
2025-10-16 00:00:00
重命名 KNOWLEDGE_POINT.level 为 depth，并添加 sort_order 字段
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.alter_column('KNOWLEDGE_POINT', 'level', new_column_name='depth', existing_type=sa.Integer())
    op.add_column('KNOWLEDGE_POINT', sa.Column('sort_order', sa.Integer(), nullable=True, comment='同级排序'))

def downgrade():
    op.alter_column('KNOWLEDGE_POINT', 'depth', new_column_name='level', existing_type=sa.Integer())
    op.drop_column('KNOWLEDGE_POINT', 'sort_order')
