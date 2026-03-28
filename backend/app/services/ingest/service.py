from __future__ import annotations

import base64
import json
from pathlib import Path

from app.schemas.citation import (
    CitationMention,
    CitationReviewCase,
    DocumentFormat,
    Manuscript,
    ReferenceEntry,
    SourceAsset,
)
from app.schemas.review import IngestRequest, IngestResponse
from app.services.classification.service import ContributionClassifier
from app.services.export.service import ExportService
from app.services.graph.service import GraphService
from app.services.parsers.bibtex import parse_bibtex_entries
from app.services.parsers.docx import extract_docx_text, parse_docx_citations
from app.services.parsers.latex import parse_latex_citations, parse_latex_sections
from app.services.parsers.pdf import extract_pdf_text, parse_pdf_citations
from app.services.resolution.service import PaperResolver


class IngestionService:
    def __init__(self, resolver: PaperResolver | None = None) -> None:
        self.resolver = resolver or PaperResolver()
        self.graph_service = GraphService()
        self.export_service = ExportService()
        self.classifier = ContributionClassifier()

    def ingest(self, request: IngestRequest) -> IngestResponse:
        manuscript = Manuscript(
            manuscript_id=request.manuscript_id,
            title=request.title,
            source_format=DocumentFormat.PLAIN_TEXT,
            metadata=request.metadata.copy(),
        )
        warnings: list[str] = []
        references: list[ReferenceEntry] = []
        mentions: list[CitationMention] = []
        queued_jobs = []

        for asset in request.assets:
            if asset.format is DocumentFormat.BIBTEX:
                references.extend(parse_bibtex_entries(asset.content))
            elif asset.format is DocumentFormat.LATEX:
                manuscript.source_format = DocumentFormat.LATEX
                manuscript.raw_text += f"\n{asset.content}"
                manuscript.sections.extend(parse_latex_sections(asset.content))
                mentions.extend(parse_latex_citations(asset.content))
            elif asset.format is DocumentFormat.DOCX:
                manuscript.source_format = DocumentFormat.DOCX
                text = extract_docx_text(_asset_bytes(asset))
                manuscript.raw_text += f"\n{text}"
                mentions.extend(parse_docx_citations(text))
            elif asset.format is DocumentFormat.PDF:
                manuscript.source_format = DocumentFormat.PDF
                text = extract_pdf_text(_asset_bytes(asset))
                manuscript.raw_text += f"\n{text}"
                mentions.extend(parse_pdf_citations(text))
                queued_jobs.extend(self.classifier.job_planner.plan_pdf_fallback_jobs(asset))
            elif asset.format is DocumentFormat.METADATA_JSON:
                parsed_references = _parse_metadata_json(asset.content)
                references.extend(parsed_references)
            else:
                manuscript.raw_text += f"\n{asset.content}"

        manuscript.references = _dedupe_references(references)
        manuscript.citations = mentions

        canonical_papers = []
        decisions = []
        for mention in mentions:
            reference_id = mention.reference_keys[0] if mention.reference_keys else None
            matched_reference = _lookup_reference(manuscript.references, reference_id)
            if matched_reference:
                candidates = self.resolver.resolve_reference(matched_reference)
                if candidates:
                    canonical_papers.append(candidates[0].paper)
                    classified = self.classifier.classify(
                        mention,
                        reference=matched_reference,
                        canonical_paper_id=candidates[0].paper.paper_id,
                        resolution_score=candidates[0].score,
                    )
                    decision = classified.decision
                    decision.metadata["resolution_source"] = candidates[0].source
                    queued_jobs.extend(classified.queued_jobs)
                    decisions.append(decision)
                    continue
            warnings.append(f"Citation {mention.mention_id} could not be resolved confidently.")
            classified = self.classifier.classify(mention, reference=matched_reference)
            decisions.append(classified.decision)
            queued_jobs.extend(classified.queued_jobs)

        case = CitationReviewCase(
            manuscript=manuscript,
            canonical_papers=_dedupe_papers(canonical_papers),
            decisions=decisions,
        )
        return IngestResponse(case=case, warnings=warnings, queued_jobs=queued_jobs)

    def export(self, case: CitationReviewCase):
        graph = self.graph_service.build_snapshot(case)
        return self.export_service.build_bundle(case, graph)


def _asset_bytes(asset: SourceAsset) -> bytes:
    if asset.media_type == "application/base64":
        return base64.b64decode(asset.content)
    return asset.content.encode("utf-8", errors="ignore")


def _parse_metadata_json(content: str) -> list[ReferenceEntry]:
    payload = json.loads(content)
    references = payload.get("references", payload if isinstance(payload, list) else [])
    parsed: list[ReferenceEntry] = []
    for index, item in enumerate(references, start=1):
        parsed.append(
            ReferenceEntry(
                reference_id=item.get("id", f"ref-{index}"),
                raw_text=item.get("raw_text") or item.get("title", ""),
                title=item.get("title"),
                authors=item.get("authors", []),
                year=item.get("year"),
                venue=item.get("venue"),
                doi=item.get("doi"),
                url=item.get("url"),
                source_key=item.get("source_key"),
                metadata={key: value for key, value in item.items() if key not in {"title", "authors", "year", "venue", "doi", "url"}},
            )
        )
    return parsed


def _dedupe_references(references: list[ReferenceEntry]) -> list[ReferenceEntry]:
    seen: dict[str, ReferenceEntry] = {}
    for reference in references:
        key = reference.doi or reference.source_key or reference.reference_id or reference.title or str(len(seen))
        seen[key] = reference
    return list(seen.values())


def _dedupe_papers(papers):
    seen = {}
    for paper in papers:
        seen[paper.paper_id] = paper
    return list(seen.values())


def _lookup_reference(references: list[ReferenceEntry], reference_key: str | None) -> ReferenceEntry | None:
    if not reference_key:
        return None
    normalized = Path(reference_key).stem.lower()
    for reference in references:
        if reference.reference_id.lower() == normalized or (reference.source_key or "").lower() == normalized:
            return reference
    for reference in references:
        if normalized in reference.reference_id.lower():
            return reference
    return None
