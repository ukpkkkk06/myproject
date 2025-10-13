"""set default for version_no on QUESTION_VERSION

Revision ID: b3d874edf9d3
Revises: aeec0cd06ff3
Create Date: 2025-10-13 08:55:32.471886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3d874edf9d3'
down_revision: Union[str, Sequence[str], None] = 'aeec0cd06ff3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
