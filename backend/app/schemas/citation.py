from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DocumentFormat(str, Enum):
    LATEX = "latex"
    BIBTEX = "bibtex"
    DOCX = "docx"
    PDF = "pdf"
    METADATA_JSON = "metadata_json"
    PLAIN_TEXT = "plain_text"


class ContributionType(str, Enum):
    BASELINE_METHOD = "baseline_method"
    DATASET_BENCHMARK = "dataset_benchmark"
    MODEL_ARCHITECTURE = "model_architecture"
    THEOREM_PROOF = "theorem_proof"
    IMPLEMENTATION_TOOLING = "implementation_tooling"
    NEGATIVE_COMPARISON = "negative_comparison"
    BACKGROUND_SURVEY = "background_survey"
    SUPPORTING_EVIDENCE = "supporting_evidence"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class EvidenceSpan:
    text: str
    start: int | None = None
    end: int | None = None
    section: str | None = None


@dataclass(slots=True)
class SourceAsset:
    filename: str
    content: str
    format: DocumentFormat
    media_type: str | None = None


@dataclass(slots=True)
class ReferenceEntry:
    reference_id: str
    raw_text: str
    title: str | None = None
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    url: str | None = None
    source_key: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CitationMention:
    mention_id: str
    marker: str
    context: str
    reference_keys: list[str] = field(default_factory=list)
    section: str | None = None
    sentence: str | None = None
    evidence: list[EvidenceSpan] = field(default_factory=list)


@dataclass(slots=True)
class AuthorIdentity:
    author_id: str
    display_name: str
    openalex_id: str | None = None
    orcid: str | None = None
    aliases: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass(slots=True)
class CanonicalPaper:
    paper_id: str
    title: str
    authors: list[AuthorIdentity] = field(default_factory=list)
    doi: str | None = None
    openalex_id: str | None = None
    crossref_id: str | None = None
    year: int | None = None
    venue: str | None = None
    abstract: str | None = None
    aliases: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CitationDecision:
    mention_id: str
    reference_id: str | None = None
    canonical_paper_id: str | None = None
    contribution_type: ContributionType = ContributionType.UNKNOWN
    confidence: float = 0.0
    evidence: list[EvidenceSpan] = field(default_factory=list)
    rationale: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Manuscript:
    manuscript_id: str
    title: str | None = None
    abstract: str | None = None
    source_format: DocumentFormat = DocumentFormat.PLAIN_TEXT
    sections: list[str] = field(default_factory=list)
    citations: list[CitationMention] = field(default_factory=list)
    references: list[ReferenceEntry] = field(default_factory=list)
    raw_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CitationReviewCase:
    manuscript: Manuscript
    canonical_papers: list[CanonicalPaper] = field(default_factory=list)
    decisions: list[CitationDecision] = field(default_factory=list)


def to_dict(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: to_dict(item) for key, item in value.items()}
    return value
