from __future__ import annotations

from dataclasses import dataclass

from app.schemas.citation import CitationDecision, CitationMention, ReferenceEntry
from app.queue.jobs import LocalJobPlanner
from app.services.classification.rules import decision_from_classification


@dataclass(slots=True)
class ClassifiedDecision:
    decision: CitationDecision
    queued_jobs: list[dict]


class ContributionClassifier:
    def __init__(self, low_confidence_threshold: float = 0.7) -> None:
        self.low_confidence_threshold = low_confidence_threshold
        self.job_planner = LocalJobPlanner()

    def classify(
        self,
        mention: CitationMention,
        reference: ReferenceEntry | None = None,
        section: str | None = None,
        canonical_paper_id: str | None = None,
        resolution_score: float | None = None,
    ) -> ClassifiedDecision:
        decision = decision_from_classification(mention, reference.reference_id if reference else None, section=section)
        decision.canonical_paper_id = canonical_paper_id
        if resolution_score is not None:
            decision.confidence = min(0.99, (decision.confidence + resolution_score) / 2)

        queued_jobs: list[dict] = []
        if reference and (resolution_score is None or decision.confidence < self.low_confidence_threshold):
            queued_jobs.append(
                self.job_planner.plan_ambiguous_resolution_job(
                    mention.mention_id,
                    reference.title or reference.raw_text,
                )
            )
        return ClassifiedDecision(decision=decision, queued_jobs=queued_jobs)
