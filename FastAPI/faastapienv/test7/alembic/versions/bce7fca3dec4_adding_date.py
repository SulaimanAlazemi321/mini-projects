"""adding date

Revision ID: bce7fca3dec4
Revises: c96f31fd95f5
Create Date: 2025-09-14 12:56:37.558459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bce7fca3dec4'
down_revision: Union[str, Sequence[str], None] = 'c96f31fd95f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("reflection",sa.Column("date", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
