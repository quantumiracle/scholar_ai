from __future__ import annotations

from app.schemas.citation import CitationReviewCase, to_dict
from app.schemas.graph import CitationGraphSnapshot, ExportBundle


class ExportService:
    def build_bundle(self, case: CitationReviewCase, graph: CitationGraphSnapshot) -> ExportBundle:
        json_document = {
            "manuscript": to_dict(case.manuscript),
            "canonical_papers": to_dict(case.canonical_papers),
            "decisions": to_dict(case.decisions),
            "graph": to_dict(graph),
        }
        return ExportBundle(
            json_document=json_document,
            bibtex=self._to_bibtex(case),
            report_markdown=self._to_report(case, graph),
            graph_snapshot=graph,
        )

    def _to_bibtex(self, case: CitationReviewCase) -> str:
        chunks: list[str] = []
        for paper in case.canonical_papers:
            key = (paper.doi or paper.paper_id).replace("/", "_").replace(":", "_")
            authors = " and ".join(author.display_name for author in paper.authors)
            chunks.append(
                "\n".join(
                    [
                        f"@article{{{key},",
                        f"  title = {{{paper.title}}},",
                        f"  author = {{{authors}}},",
                        f"  year = {{{paper.year or ''}}},",
                        f"  journal = {{{paper.venue or ''}}},",
                        f"  doi = {{{paper.doi or ''}}},",
                        "}",
                    ]
                )
            )
        return "\n\n".join(chunks)

    def _to_report(self, case: CitationReviewCase, graph: CitationGraphSnapshot) -> str:
        unresolved = [decision for decision in case.decisions if not decision.canonical_paper_id]
        lines = [
            "# Citation Review Report",
            "",
            f"- Manuscript: `{case.manuscript.manuscript_id}`",
            f"- References: `{len(case.manuscript.references)}`",
            f"- Citation mentions: `{len(case.manuscript.citations)}`",
            f"- Resolved citation links: `{graph.metrics['resolved_citation_count']}`",
            f"- Unresolved citation links: `{len(unresolved)}`",
            "",
            "## Unresolved Mentions",
        ]
        if unresolved:
            for decision in unresolved:
                lines.append(f"- `{decision.mention_id}`: {decision.rationale or 'Needs reviewer attention.'}")
        else:
            lines.append("- None")
        return "\n".join(lines)
