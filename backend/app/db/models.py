from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ManuscriptRecord(Base):
    __tablename__ = "manuscripts"

    manuscript_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_format: Mapped[str] = mapped_column(String(32), default="plain_text")
    raw_text: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

    references: Mapped[list["ReferenceRecord"]] = relationship(back_populates="manuscript")
    decisions: Mapped[list["CitationDecisionRecord"]] = relationship(back_populates="manuscript")


class ReferenceRecord(Base):
    __tablename__ = "reference_entries"

    reference_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    manuscript_id: Mapped[str] = mapped_column(ForeignKey("manuscripts.manuscript_id"))
    raw_text: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    authors_json: Mapped[list] = mapped_column("authors", JSON, default=list)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(512), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

    manuscript: Mapped["ManuscriptRecord"] = relationship(back_populates="references")


class CanonicalPaperRecord(Base):
    __tablename__ = "canonical_papers"

    paper_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    title: Mapped[str] = mapped_column(String(1024))
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    openalex_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crossref_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(512), nullable=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    aliases_json: Mapped[list] = mapped_column("aliases", JSON, default=list)
    provenance_json: Mapped[dict] = mapped_column("provenance", JSON, default=dict)


class CitationDecisionRecord(Base):
    __tablename__ = "citation_decisions"

    decision_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manuscript_id: Mapped[str] = mapped_column(ForeignKey("manuscripts.manuscript_id"))
    mention_id: Mapped[str] = mapped_column(String(128))
    reference_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    canonical_paper_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contribution_type: Mapped[str] = mapped_column(String(64), default="unknown")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[list] = mapped_column("evidence", JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

    manuscript: Mapped["ManuscriptRecord"] = relationship(back_populates="decisions")
