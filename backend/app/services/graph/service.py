from __future__ import annotations

from app.schemas.citation import CitationReviewCase
from app.schemas.graph import CitationGraphSnapshot, GraphEdge, GraphNode, IndexRecord


class GraphService:
    def build_snapshot(self, case: CitationReviewCase) -> CitationGraphSnapshot:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        manuscript = case.manuscript
        nodes.append(
            GraphNode(
                node_id=manuscript.manuscript_id,
                node_type="manuscript",
                label=manuscript.title or manuscript.manuscript_id,
                properties={"source_format": manuscript.source_format.value},
            )
        )

        for reference in manuscript.references:
            nodes.append(
                GraphNode(
                    node_id=reference.reference_id,
                    node_type="reference_entry",
                    label=reference.title or reference.reference_id,
                    properties={"doi": reference.doi, "year": reference.year},
                )
            )
            edges.append(
                GraphEdge(
                    source=manuscript.manuscript_id,
                    target=reference.reference_id,
                    edge_type="references",
                )
            )

        for paper in case.canonical_papers:
            nodes.append(
                GraphNode(
                    node_id=paper.paper_id,
                    node_type="canonical_paper",
                    label=paper.title,
                    properties={"doi": paper.doi, "year": paper.year, "venue": paper.venue},
                )
            )
            for author in paper.authors:
                nodes.append(
                    GraphNode(
                        node_id=author.author_id,
                        node_type="author",
                        label=author.display_name,
                        properties={"openalex_id": author.openalex_id, "confidence": author.confidence},
                    )
                )
                edges.append(
                    GraphEdge(
                        source=paper.paper_id,
                        target=author.author_id,
                        edge_type="authored_by",
                    )
                )

        paper_by_id = {paper.paper_id: paper for paper in case.canonical_papers}
        for decision in case.decisions:
            if not decision.canonical_paper_id:
                continue
            paper = paper_by_id.get(decision.canonical_paper_id)
            if not paper:
                continue
            edges.append(
                GraphEdge(
                    source=manuscript.manuscript_id,
                    target=paper.paper_id,
                    edge_type="cites",
                    properties={
                        "mention_id": decision.mention_id,
                        "contribution_type": decision.contribution_type.value,
                        "confidence": decision.confidence,
                    },
                )
            )

        metrics = {
            "reference_count": len(manuscript.references),
            "citation_count": len(manuscript.citations),
            "resolved_citation_count": sum(1 for item in case.decisions if item.canonical_paper_id),
            "canonical_paper_count": len(case.canonical_papers),
        }
        return CitationGraphSnapshot(
            graph_id=f"graph:{manuscript.manuscript_id}",
            nodes=_dedupe_nodes(nodes),
            edges=edges,
            metrics=metrics,
        )

    def build_index_records(self, case: CitationReviewCase) -> list[IndexRecord]:
        paper_by_id = {paper.paper_id: paper for paper in case.canonical_papers}
        records: list[IndexRecord] = []
        for decision in case.decisions:
            if not decision.canonical_paper_id:
                continue
            paper = paper_by_id.get(decision.canonical_paper_id)
            if not paper:
                continue
            records.append(
                IndexRecord(
                    record_id=f"{case.manuscript.manuscript_id}:{decision.mention_id}",
                    manuscript_id=case.manuscript.manuscript_id,
                    paper_id=paper.paper_id,
                    contribution_type=decision.contribution_type.value,
                    confidence=decision.confidence,
                    doi=paper.doi,
                    author_names=[author.display_name for author in paper.authors],
                )
            )
        return records


def _dedupe_nodes(nodes: list[GraphNode]) -> list[GraphNode]:
    seen: dict[str, GraphNode] = {}
    for node in nodes:
        seen[node.node_id] = node
    return list(seen.values())
