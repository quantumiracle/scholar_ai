from __future__ import annotations

import re

from app.schemas.citation import ReferenceEntry


ENTRY_START_RE = re.compile(r"@(?P<kind>\w+)\s*\{\s*(?P<key>[^,]+),", re.DOTALL)
FIELD_RE = re.compile(r"(?P<name>\w+)\s*=\s*(?P<value>\{(?:[^{}]|\{[^{}]*\})*\}|\".*?\"|\d+)", re.DOTALL)


def parse_bibtex_entries(text: str) -> list[ReferenceEntry]:
    entries: list[ReferenceEntry] = []
    for kind, key, body, raw_entry in _iter_entries(text):
        fields = {
            field.group("name").lower(): " ".join(_strip_wrappers(field.group("value")).split())
            for field in FIELD_RE.finditer(body)
        }
        year = _maybe_int(fields.get("year"))
        authors = _parse_authors(fields.get("author", ""))
        entries.append(
            ReferenceEntry(
                reference_id=key,
                source_key=key,
                raw_text=raw_entry.strip(),
                title=fields.get("title"),
                authors=authors,
                year=year,
                venue=fields.get("journal") or fields.get("booktitle"),
                doi=_normalize_doi(fields.get("doi")),
                url=fields.get("url"),
                metadata={"entry_type": kind.lower(), "fields": fields},
            )
        )
    return entries


def _parse_authors(author_field: str) -> list[str]:
    parts = [part.strip() for part in author_field.split(" and ") if part.strip()]
    return [" ".join(part.replace(",", " ").split()) for part in parts]


def _maybe_int(value: str | None) -> int | None:
    if not value:
        return None
    digits = re.findall(r"\d{4}", value)
    return int(digits[0]) if digits else None


def _normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip().removeprefix("https://doi.org/").removeprefix("doi:")
    return cleaned or None


def _iter_entries(text: str):
    for match in ENTRY_START_RE.finditer(text):
        depth = 1
        index = match.end()
        while index < len(text) and depth > 0:
            char = text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            index += 1
        raw_entry = text[match.start():index]
        body = text[match.end():index - 1]
        yield match.group("kind"), match.group("key").strip(), body, raw_entry


def _strip_wrappers(value: str) -> str:
    value = value.strip()
    if (value.startswith("{") and value.endswith("}")) or (value.startswith('"') and value.endswith('"')):
        return value[1:-1]
    return value
