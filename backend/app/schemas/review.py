from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.schemas.citation import CitationReviewCase, SourceAsset


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_HUMAN = "needs_human"


@dataclass(slots=True)
class ReviewAction:
    action_id: str
    manuscript_id: str
    citation_id: str
    actor: str
    status: ReviewStatus
    note: str | None = None
    chosen_paper_id: str | None = None
    chosen_label: str | None = None


@dataclass(slots=True)
class IngestRequest:
    manuscript_id: str
    title: str | None = None
    assets: list[SourceAsset] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IngestResponse:
    case: CitationReviewCase
    warnings: list[str] = field(default_factory=list)
    queued_jobs: list[dict[str, Any]] = field(default_factory=list)
