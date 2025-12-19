"""create table ErrorDataQuality

Revision ID: 84c42739c17b
Revises: b031206324b7
Create Date: 2025-12-10 13:57:55.869834

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "84c42739c17b"
down_revision: Union[str, None] = "b031206324b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "error_data_quality",
        sa.Column(
            "id", sa.Uuid(), server_default=text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("slice_id", sa.Uuid(), nullable=True),
        sa.Column("error_raiser", sa.String(), nullable=False),
        sa.Column("error_info", sa.String(), nullable=False),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), server_default="NOW()", nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["document_related.welearn_document.id"],
            name="error_data_quality_document_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["slice_id"],
            ["document_related.document_slice.id"],
            name="error_data_quality_slice_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="document_related",
    )


def downgrade() -> None:

    op.drop_table("error_data_quality", schema="document_related")
