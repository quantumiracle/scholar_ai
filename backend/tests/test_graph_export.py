from __future__ import annotations

import unittest

from app.schemas.citation import (
    AuthorIdentity,
    CanonicalPaper,
    CitationDecision,
    CitationMention,
    CitationReviewCase,
    ContributionType,
    DocumentFormat,
    Manuscript,
    ReferenceEntry,
)
from app.services.export.service import ExportService
from app.services.graph.service import GraphService


class GraphExportTests(unittest.TestCase):
    def test_graph_and_export_bundle(self) -> None:
        case = CitationReviewCase(
            manuscript=Manuscript(
                manuscript_id="m-1",
                title="A Paper",
                source_format=DocumentFormat.LATEX,
                citations=[CitationMention(mention_id="c-1", marker="\\cite{x}", context="We use a benchmark.", reference_keys=["ref-1"])],
                references=[ReferenceEntry(reference_id="ref-1", raw_text="raw", title="Benchmark Paper", year=2023)],
            ),
            canonical_papers=[
                CanonicalPaper(
                    paper_id="paper-1",
                    title="Benchmark Paper",
                    year=2023,
                    authors=[AuthorIdentity(author_id="author-1", display_name="Jane Doe", confidence=0.8)],
                )
            ],
            decisions=[
                CitationDecision(
                    mention_id="c-1",
                    reference_id="ref-1",
                    canonical_paper_id="paper-1",
                    contribution_type=ContributionType.DATASET_BENCHMARK,
                    confidence=0.88,
                )
            ],
        )
        graph = GraphService().build_snapshot(case)
        index_records = GraphService().build_index_records(case)
        bundle = ExportService().build_bundle(case, graph)

        self.assertEqual(graph.metrics["resolved_citation_count"], 1)
        self.assertEqual(index_records[0].paper_id, "paper-1")
        self.assertIn("@article", bundle.bibtex)
        self.assertIn("Citation Review Report", bundle.report_markdown)
        self.assertEqual(bundle.json_document["graph"]["metrics"]["reference_count"], 1)


if __name__ == "__main__":
    unittest.main()
