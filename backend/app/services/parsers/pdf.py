from __future__ import annotations

from io import BytesIO
import re

from app.schemas.citation import CitationMention, EvidenceSpan


INLINE_NUMERIC_RE = re.compile(r"\[(?P<label>\d+(?:\s*,\s*\d+)*)\]")
INLINE_AUTHOR_YEAR_RE = re.compile(r"\((?P<label>[A-Z][A-Za-z\-]+(?: et al\.)?,?\s+\d{4}[a-z]?)\)")


def extract_pdf_text(raw_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return raw_bytes.decode("utf-8", errors="ignore")

    reader = PdfReader(BytesIO(raw_bytes))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def parse_pdf_citations(text: str) -> list[CitationMention]:
    mentions: list[CitationMention] = []
    for index, match in enumerate(_iter_matches(text), start=1):
        context = _extract_context(text, match.start(), match.end())
        mentions.append(
            CitationMention(
                mention_id=f"pdf-cite-{index}",
                marker=match.group(0),
                context=context,
                reference_keys=[value.strip() for value in match.group("label").split(",")],
                sentence=context,
                evidence=[EvidenceSpan(text=context, start=match.start(), end=match.end())],
            )
        )
    return mentions


def _iter_matches(text: str):
    yield from INLINE_NUMERIC_RE.finditer(text)
    yield from INLINE_AUTHOR_YEAR_RE.finditer(text)


def _extract_context(text: str, start: int, end: int, window: int = 160) -> str:
    lo = max(0, start - window)
    hi = min(len(text), end + window)
    return " ".join(text[lo:hi].split())
