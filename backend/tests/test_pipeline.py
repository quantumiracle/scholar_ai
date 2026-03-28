from __future__ import annotations

import unittest

from app.schemas.citation import (
    AuthorIdentity,
    CanonicalPaper,
    CitationMention,
    ContributionType,
    DocumentFormat,
    ReferenceEntry,
    SourceAsset,
)
from app.schemas.review import IngestRequest
from app.services.classification.rules import classify_mention
from app.services.ingest.service import IngestionService
from app.services.resolution.service import ResolutionCandidate


class FakeResolver:
    def resolve_reference(self, reference: ReferenceEntry):
        if reference.title and "Attention" in reference.title:
            return [
                ResolutionCandidate(
                    paper=CanonicalPaper(
                        paper_id="doi:10.48550/arXiv.1706.03762",
                        title="Attention Is All You Need",
                        doi="10.48550/arXiv.1706.03762",
                        year=2017,
                        venue="NeurIPS",
                        authors=[AuthorIdentity(author_id="author:1", display_name="Ashish Vaswani", confidence=0.9)],
                    ),
                    score=0.96,
                    source="fake:test",
                )
            ]
        return []


class PipelineTests(unittest.TestCase):
    def test_ingestion_builds_case_and_exports(self) -> None:
        request = IngestRequest(
            manuscript_id="paper-1",
            title="Test Paper",
            assets=[
                SourceAsset(
                    filename="paper.tex",
                    format=DocumentFormat.LATEX,
                    content=r"\section{Methods} We adopt the Transformer backbone \cite{vaswani2017attention}.",
                ),
                SourceAsset(
                    filename="refs.bib",
                    format=DocumentFormat.BIBTEX,
                    content="""
                    @article{vaswani2017attention,
                      title={Attention Is All You Need},
                      author={Vaswani, Ashish},
                      year={2017},
                      journal={NeurIPS},
                      doi={10.48550/arXiv.1706.03762}
                    }
                    """,
                ),
            ],
        )
        service = IngestionService(resolver=FakeResolver())
        response = service.ingest(request)
        bundle = service.export(response.case)

        self.assertEqual(len(response.case.manuscript.references), 1)
        self.assertEqual(len(response.case.decisions), 1)
        self.assertEqual(response.case.decisions[0].canonical_paper_id, "doi:10.48550/arXiv.1706.03762")
        self.assertIn("Attention Is All You Need", bundle.bibtex)
        self.assertEqual(bundle.graph_snapshot.metrics["resolved_citation_count"], 1)

    def test_classification_prefers_model_architecture(self) -> None:
        mention = CitationMention(
            mention_id="c-1",
            marker="\\cite{x}",
            context="We use the transformer encoder architecture proposed in prior work.",
            sentence="We use the transformer encoder architecture proposed in prior work.",
        )
        result = classify_mention(mention, section="Methods")
        self.assertEqual(result.contribution, ContributionType.MODEL_ARCHITECTURE)
        self.assertGreater(result.confidence, 0.5)

    def test_unresolved_reference_queues_gpu_rerank(self) -> None:
        request = IngestRequest(
            manuscript_id="paper-2",
            assets=[
                SourceAsset(
                    filename="paper.tex",
                    format=DocumentFormat.LATEX,
                    content=r"\section{Results} We compare with prior work \cite{unknown2024}.",
                ),
                SourceAsset(
                    filename="refs.bib",
                    format=DocumentFormat.BIBTEX,
                    content="""
                    @article{unknown2024,
                      title={A Difficult Reference To Resolve},
                      author={Doe, Jane},
                      year={2024},
                      journal={ArXiv}
                    }
                    """,
                ),
            ],
        )
        service = IngestionService(resolver=FakeResolver())
        response = service.ingest(request)
        self.assertEqual(response.queued_jobs[0]["job_type"], "citation_rerank")


if __name__ == "__main__":
    unittest.main()
