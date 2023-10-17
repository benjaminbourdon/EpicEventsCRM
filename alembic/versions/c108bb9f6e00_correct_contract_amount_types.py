"""correct contract amount types

Revision ID: c108bb9f6e00
Revises: 7bea40c4a323
Create Date: 2023-10-16 12:29:22.766131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c108bb9f6e00'
down_revision: Union[str, None] = '7bea40c4a323'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
