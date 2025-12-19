"""create column external_id

Revision ID: ccdbd708c997
Revises: b031206324b7
Create Date: 2025-12-11 11:11:49.611995

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from welearn_database.data.enumeration import ExternalIdType

# revision identifiers, used by Alembic.
revision: str = "ccdbd708c997"
down_revision: Union[str, None] = "b031206324b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajout des colonnes external_id et external_id_type à la table welearn_document
    op.add_column(
        "welearn_document",
        sa.Column("external_id", sa.String(), nullable=True),
        schema="document_related",
    )

    # Correction : construction correcte de la chaîne pour l'enum PostgreSQL
    enum_string = ",".join([f"'{i.value.lower()}'" for i in ExternalIdType])
    op.execute(
        f"CREATE TYPE document_related.external_id_type AS ENUM ({enum_string});"
    )
    op.add_column(
        "welearn_document",
        sa.Column(
            "external_id_type",
            postgresql.ENUM(
                *(e.value.lower() for e in ExternalIdType),
                name="external_id_type",
                schema="document_related",
            ),
            nullable=True,
        ),
        schema="document_related",
    )


def downgrade() -> None:
    # Suppression des colonnes external_id et external_id_type de la table welearn_document
    op.drop_column("welearn_document", "external_id", schema="document_related")
    op.drop_column("welearn_document", "external_id_type", schema="document_related")
    op.execute("DROP TYPE external_id_type;")
