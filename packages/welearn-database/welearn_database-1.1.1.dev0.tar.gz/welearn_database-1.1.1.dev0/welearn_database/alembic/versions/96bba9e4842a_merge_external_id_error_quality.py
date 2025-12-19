"""Merge dev versions

Revision ID: 96bba9e4842a
Revises: 84c42739c17b, ccdbd708c997
Create Date: 2025-12-11 11:20:19.646404

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "96bba9e4842a"
down_revision: Union[str, None] = ("84c42739c17b", "ccdbd708c997")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
