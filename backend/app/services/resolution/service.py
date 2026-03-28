from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from app.schemas.citation import AuthorIdentity, CanonicalPaper, ReferenceEntry
from app.services.providers.crossref import CrossrefClient
from app.services.providers.openalex import OpenAlexClient


@dataclass(slots=True)
class ResolutionCandidate:
    paper: CanonicalPaper
    score: float
    source: str


class PaperResolver:
    def __init__(
        self,
        crossref: CrossrefClient | None = None,
        openalex: OpenAlexClient | None = None,
    ) -> None:
        self.crossref = crossref or CrossrefClient()
        self.openalex = openalex or OpenAlexClient()

    def resolve_reference(self, reference: ReferenceEntry) -> list[ResolutionCandidate]:
        candidates: list[ResolutionCandidate] = []
        if reference.doi:
            crossref_work = _safe_lookup(lambda: self.crossref.get_by_doi(reference.doi))
            if crossref_work:
                candidates.append(
                    ResolutionCandidate(
                        paper=_paper_from_crossref(crossref_work),
                        score=0.99,
                        source="crossref:doi",
                    )
                )
            openalex_work = _safe_lookup(lambda: self.openalex.get_by_doi(reference.doi))
            if openalex_work:
                candidates.append(
                    ResolutionCandidate(
                        paper=_paper_from_openalex(openalex_work),
                        score=0.98,
                        source="openalex:doi",
                    )
                )
        if reference.title:
            candidates.extend(self._search_by_title(reference))
        deduped: dict[str, ResolutionCandidate] = {}
        for candidate in sorted(candidates, key=lambda item: item.score, reverse=True):
            existing = deduped.get(candidate.paper.paper_id)
            if not existing or existing.score < candidate.score:
                deduped[candidate.paper.paper_id] = candidate
        return list(deduped.values())

    def _search_by_title(self, reference: ReferenceEntry) -> list[ResolutionCandidate]:
        results: list[ResolutionCandidate] = []
        for work in _safe_lookup(lambda: self.crossref.search(reference.title or ""), default=[]):
            results.append(
                ResolutionCandidate(
                    paper=_paper_from_crossref(work),
                    score=_score_candidate(reference, work.title, work.year, work.authors),
                    source="crossref:title",
                )
            )
        for work in _safe_lookup(lambda: self.openalex.search(reference.title or ""), default=[]):
            results.append(
                ResolutionCandidate(
                    paper=_paper_from_openalex(work),
                    score=_score_candidate(
                        reference,
                        work.title,
                        work.year,
                        [(authorship.get("author") or {}).get("display_name", "") for authorship in work.authors],
                    ),
                    source="openalex:title",
                )
            )
        return results


def _score_candidate(
    reference: ReferenceEntry,
    title: str,
    year: int | None,
    candidate_authors: list[str] | None = None,
) -> float:
    title_score = SequenceMatcher(None, (reference.title or "").lower(), title.lower()).ratio()
    year_bonus = 0.1 if reference.year and reference.year == year else 0.0
    doi_bonus = 0.15 if reference.doi else 0.0
    author_bonus = 0.08 if _author_overlap(reference, candidate_authors or []) else 0.0
    return round(min(title_score + year_bonus + doi_bonus + author_bonus, 0.97), 4)


def _paper_from_crossref(work) -> CanonicalPaper:
    authors = [
        AuthorIdentity(author_id=f"author:{index}", display_name=name, confidence=0.8)
        for index, name in enumerate(work.authors, start=1)
    ]
    return CanonicalPaper(
        paper_id=f"doi:{work.doi or work.title}",
        title=work.title,
        doi=work.doi,
        year=work.year,
        venue=work.venue,
        authors=authors,
        provenance={"source": "crossref", "raw": work.raw},
    )


def _paper_from_openalex(work) -> CanonicalPaper:
    authors = [
        AuthorIdentity(
            author_id=(authorship.get("author") or {}).get("id", f"author:{index}"),
            display_name=(authorship.get("author") or {}).get("display_name", f"Author {index}"),
            openalex_id=(authorship.get("author") or {}).get("id"),
            confidence=0.85,
        )
        for index, authorship in enumerate(work.authors, start=1)
    ]
    return CanonicalPaper(
        paper_id=work.work_id or f"paper:{work.title}",
        title=work.title,
        doi=work.doi,
        openalex_id=work.work_id,
        year=work.year,
        venue=work.venue,
        authors=authors,
        provenance={"source": "openalex", "raw": work.raw},
    )


def _safe_lookup(callback, default=None):
    try:
        return callback()
    except Exception:
        return default


def _author_overlap(reference: ReferenceEntry, candidate_authors: list[str]) -> bool:
    if not reference.authors:
        return False
    haystack = " ".join(candidate_authors).lower()
    for author in reference.authors:
        surname = author.split()[-1].lower()
        if surname and surname in haystack:
            return True
    return False
