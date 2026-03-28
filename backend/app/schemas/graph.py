from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GraphNode:
    node_id: str
    node_type: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GraphEdge:
    source: str
    target: str
    edge_type: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CitationGraphSnapshot:
    graph_id: str
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExportBundle:
    json_document: dict[str, Any]
    bibtex: str
    report_markdown: str
    graph_snapshot: CitationGraphSnapshot


@dataclass(slots=True)
class IndexRecord:
    record_id: str
    manuscript_id: str
    paper_id: str
    contribution_type: str
    confidence: float
    doi: str | None = None
    author_names: list[str] = field(default_factory=list)
