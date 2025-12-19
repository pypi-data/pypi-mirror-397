"""doc qty per source

Revision ID: 0e0bc0fca384
Revises: 96bba9e4842a
Create Date: 2025-12-18 15:27:02.973026

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0e0bc0fca384"
down_revision: Union[str, None] = "96bba9e4842a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE MATERIALIZED VIEW document_related.qty_document_in_qdrant_per_corpus
        AS 
        (SELECT
            source_name,
            COUNT(1)
        FROM
            grafana.test_document_latest_state tdls
        INNER JOIN corpus_related.corpus c ON
            c.id = tdls.corpus_id
        WHERE
            tdls.title = 'document_in_qdrant'
        GROUP BY
            source_name)
        WITH NO DATA;
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW document_related.qty_document_per_corpus
        AS 
        (SELECT
            source_name,
            COUNT(1)
        FROM
            grafana.test_document_latest_state tdls
        INNER JOIN corpus_related.corpus c ON
            c.id = tdls.corpus_id
        GROUP BY
            source_name)
        WITH NO DATA;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP MATERIALIZED VIEW document_related.qty_document_in_qdrant_per_corpus;
        """
    )

    op.execute(
        """
        DROP MATERIALIZED VIEW document_related.qty_document_per_corpus;
        """
    )
