from __future__ import annotations

import re
from itertools import count

from app.schemas.citation import CitationMention, EvidenceSpan


CITE_RE = re.compile(r"\\cite[t|p]?\*?(?:\[[^\]]*\])?\{(?P<keys>[^}]+)\}")
SECTION_RE = re.compile(r"\\(?:section|subsection|subsubsection)\{(?P<title>[^}]+)\}")


def parse_latex_sections(text: str) -> list[str]:
    return [match.group("title").strip() for match in SECTION_RE.finditer(text)]


def parse_latex_citations(text: str) -> list[CitationMention]:
    mentions: list[CitationMention] = []
    ids = count(1)
    for match in CITE_RE.finditer(text):
        keys = [key.strip() for key in match.group("keys").split(",") if key.strip()]
        context = _extract_context(text, match.start(), match.end())
        mentions.append(
            CitationMention(
                mention_id=f"cite-{next(ids)}",
                marker=match.group(0),
                context=context,
                reference_keys=keys,
                sentence=context,
                evidence=[EvidenceSpan(text=context, start=match.start(), end=match.end())],
            )
        )
    return mentions


def _extract_context(text: str, start: int, end: int, window: int = 160) -> str:
    lo = max(0, start - window)
    hi = min(len(text), end + window)
    return " ".join(text[lo:hi].split())
