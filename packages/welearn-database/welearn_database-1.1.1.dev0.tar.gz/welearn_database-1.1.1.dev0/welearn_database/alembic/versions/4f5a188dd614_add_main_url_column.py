"""add main url column

Revision ID: 4f5a188dd614
Revises: 0e0bc0fca384
Create Date: 2025-12-18 15:55:10.780209

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f5a188dd614"
down_revision: Union[str, None] = "0e0bc0fca384"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "corpus",
        sa.Column("main_url", sa.String(), nullable=True),
        schema="corpus_related",
    )


def downgrade() -> None:
    op.drop_column("corpus", "main_url", schema="corpus_related")
