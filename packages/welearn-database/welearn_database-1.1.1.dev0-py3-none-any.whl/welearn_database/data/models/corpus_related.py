from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, func, types
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from welearn_database.data.enumeration import DbSchemaEnum

from . import Base

schema_name = DbSchemaEnum.CORPUS_RELATED.value


class Corpus(Base):
    __tablename__ = "corpus"
    __table_args__ = {"schema": schema_name}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    source_name: Mapped[str]
    main_url: Mapped[str | None] = mapped_column(nullable=True)
    is_fix: Mapped[bool]
    binary_treshold: Mapped[float] = mapped_column(nullable=False, default=0.5)
    is_active: Mapped[bool]
    category_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(f"{schema_name}.category.id"),
    )


class Category(Base):
    __tablename__ = "category"
    __table_args__ = {"schema": schema_name}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    title: Mapped[str]


class EmbeddingModel(Base):
    __tablename__ = "embedding_model"
    __table_args__ = {"schema": schema_name}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    title: Mapped[str]
    lang: Mapped[str]


class BiClassifierModel(Base):
    __tablename__ = "bi_classifier_model"
    __table_args__ = {"schema": schema_name}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    title: Mapped[str]
    binary_treshold: Mapped[float] = mapped_column(default=0.5)
    lang: Mapped[str]
    used_since: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )


class NClassifierModel(Base):
    __tablename__ = "n_classifier_model"
    __table_args__ = {"schema": schema_name}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    title: Mapped[str]
    lang: Mapped[str]
    treshold_sdg_1: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_2: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_3: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_4: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_5: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_6: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_7: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_8: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_9: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_10: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_11: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_12: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_13: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_14: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_15: Mapped[float] = mapped_column(default=0.5)
    treshold_sdg_16: Mapped[float] = mapped_column(default=0.5)
    used_since: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )


class CorpusNameEmbeddingModelLang(Base):
    __tablename__ = "corpus_name_embedding_model_lang"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True
    source_name: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    lang: Mapped[str]


class CorpusEmbeddingModel(Base):
    __tablename__ = "corpus_embedding_model"
    __table_args__ = (
        UniqueConstraint(
            "corpus_id",
            "embedding_model_id",
            name="unique_corpus_embedding_association",
        ),
        {"schema": schema_name},
    )

    corpus_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.corpus.id"),
        primary_key=True,
    )
    embedding_model_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.embedding_model.id"),
        primary_key=True,
    )

    used_since: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )

    embedding_model: Mapped["EmbeddingModel"] = relationship()
    corpus: Mapped["Corpus"] = relationship()


class CorpusNClassifierModel(Base):
    __tablename__ = "corpus_n_classifier_model"
    __table_args__ = (
        UniqueConstraint(
            "corpus_id",
            "n_classifier_model_id",
            name="unique_corpus_n_classifier_association",
        ),
        {"schema": schema_name},
    )

    corpus_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.corpus.id"),
        primary_key=True,
    )
    n_classifier_model_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.n_classifier_model.id"),
        primary_key=True,
    )

    used_since: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )

    n_classifier_model: Mapped["NClassifierModel"] = relationship()
    corpus: Mapped["Corpus"] = relationship()


class CorpusBiClassifierModel(Base):
    __tablename__ = "corpus_bi_classifier_model"
    __table_args__ = (
        UniqueConstraint(
            "corpus_id",
            "bi_classifier_model_id",
            name="unique_corpus_bi_classifier_association",
        ),
        {"schema": schema_name},
    )

    corpus_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.corpus.id"),
        primary_key=True,
    )
    bi_classifier_model_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.bi_classifier_model.id"),
        primary_key=True,
    )
    used_since: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )

    bi_classifier_model: Mapped["BiClassifierModel"] = relationship()
    corpus: Mapped["Corpus"] = relationship()
