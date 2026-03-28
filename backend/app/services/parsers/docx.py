from __future__ import annotations

from io import BytesIO
import re
from xml.etree import ElementTree
from zipfile import ZipFile

from app.schemas.citation import CitationMention, EvidenceSpan


WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
CITATION_RE = re.compile(r"\[(?P<label>[^\]]+?\d{4}[^\]]*?)\]")


def extract_docx_text(raw_bytes: bytes) -> str:
    with ZipFile(BytesIO(raw_bytes)) as archive:
        xml_bytes = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml_bytes)
    parts = [
        node.text
        for node in root.findall(".//w:t", WORD_NS)
        if node.text
    ]
    return "\n".join(_chunk_paragraphs(parts))


def parse_docx_citations(text: str) -> list[CitationMention]:
    mentions: list[CitationMention] = []
    for index, match in enumerate(CITATION_RE.finditer(text), start=1):
        context = _extract_context(text, match.start(), match.end())
        mentions.append(
            CitationMention(
                mention_id=f"docx-cite-{index}",
                marker=match.group(0),
                context=context,
                reference_keys=[match.group("label").strip()],
                sentence=context,
                evidence=[EvidenceSpan(text=context, start=match.start(), end=match.end())],
            )
        )
    return mentions


def _chunk_paragraphs(parts: list[str], width: int = 12) -> list[str]:
    buffer: list[str] = []
    paragraphs: list[str] = []
    for part in parts:
        buffer.append(part)
        if len(buffer) >= width:
            paragraphs.append(" ".join(buffer))
            buffer.clear()
    if buffer:
        paragraphs.append(" ".join(buffer))
    return paragraphs


def _extract_context(text: str, start: int, end: int, window: int = 160) -> str:
    lo = max(0, start - window)
    hi = min(len(text), end + window)
    return " ".join(text[lo:hi].split())
