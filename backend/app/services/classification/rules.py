from __future__ import annotations

from dataclasses import dataclass

from app.schemas.citation import CitationDecision, CitationMention, ContributionType, EvidenceSpan


KEYWORD_RULES: list[tuple[ContributionType, tuple[str, ...]]] = [
    (ContributionType.DATASET_BENCHMARK, ("dataset", "benchmark", "evaluation set", "corpus")),
    (ContributionType.MODEL_ARCHITECTURE, ("architecture", "encoder", "decoder", "transformer", "backbone")),
    (ContributionType.BASELINE_METHOD, ("baseline", "following", "building on", "inspired by", "adopt")),
    (ContributionType.IMPLEMENTATION_TOOLING, ("library", "toolkit", "framework", "implementation", "codebase")),
    (ContributionType.THEOREM_PROOF, ("theorem", "lemma", "proof", "proposition", "corollary")),
    (ContributionType.NEGATIVE_COMPARISON, ("unlike", "however", "outperform", "compared with", "contrast")),
    (ContributionType.BACKGROUND_SURVEY, ("survey", "background", "overview", "historically", "prior work")),
]


@dataclass(slots=True)
class ClassificationResult:
    contribution: ContributionType
    confidence: float
    rationale: str


def classify_mention(mention: CitationMention, section: str | None = None) -> ClassificationResult:
    haystack = " ".join(filter(None, [section, mention.context, mention.sentence])).lower()
    best = ClassificationResult(
        contribution=ContributionType.UNKNOWN,
        confidence=0.25,
        rationale="No rules matched; human review recommended.",
    )
    for contribution, keywords in KEYWORD_RULES:
        hits = sum(keyword in haystack for keyword in keywords)
        if not hits:
            continue
        confidence = min(0.55 + hits * 0.1, 0.95)
        rationale = f"Matched {hits} rule keywords for {contribution.value}."
        if confidence > best.confidence:
            best = ClassificationResult(contribution=contribution, confidence=confidence, rationale=rationale)
    return best


def decision_from_classification(mention: CitationMention, reference_id: str | None, section: str | None = None) -> CitationDecision:
    result = classify_mention(mention, section=section)
    return CitationDecision(
        mention_id=mention.mention_id,
        reference_id=reference_id,
        contribution_type=result.contribution,
        confidence=result.confidence,
        rationale=result.rationale,
        evidence=[EvidenceSpan(text=mention.context, section=section)],
    )
