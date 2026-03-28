import { CitationReviewTable } from "@/components/citation-review-table";
import { ExportPanel } from "@/components/export-panel";
import { ReviewWorkbench } from "@/components/review-workbench";
import { SummaryCards } from "@/components/summary-cards";
import { UploadPanel } from "@/components/upload-panel";
import { CitationCase } from "@/lib/types";

const demoCase: CitationCase = {
  manuscript: {
    manuscript_id: "demo-manuscript",
    title: "Contribution-Aware Citation Refactoring",
    citations: [
      {
        mention_id: "cite-1",
        marker: "\\cite{vaswani2017attention}",
        context: "We adopt the Transformer backbone following prior sequence modeling work."
      },
      {
        mention_id: "cite-2",
        marker: "[3]",
        context: "Evaluation is reported on the benchmark dataset introduced in prior work."
      }
    ],
    references: [
      { reference_id: "vaswani2017attention", title: "Attention Is All You Need", doi: "10.48550/arXiv.1706.03762" },
      { reference_id: "dataset-3", title: "A Benchmark Dataset for Citation Analysis", doi: null }
    ]
  },
  canonical_papers: [
    {
      paper_id: "doi:10.48550/arXiv.1706.03762",
      title: "Attention Is All You Need",
      doi: "10.48550/arXiv.1706.03762",
      year: 2017,
      venue: "NeurIPS"
    }
  ],
  decisions: [
    {
      mention_id: "cite-1",
      reference_id: "vaswani2017attention",
      canonical_paper_id: "doi:10.48550/arXiv.1706.03762",
      contribution_type: "model_architecture",
      confidence: 0.92,
      rationale: "Detected architecture-related keywords in the citation context."
    },
    {
      mention_id: "cite-2",
      reference_id: "dataset-3",
      canonical_paper_id: null,
      contribution_type: "dataset_benchmark",
      confidence: 0.61,
      rationale: "Dataset language detected, but canonical match is unresolved."
    }
  ]
};

export default function HomePage() {
  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="eyebrow">Paper Reference Refactor System</p>
          <h1>Review citations by technical contribution before they reach indexing pipelines.</h1>
          <p className="muted">
            Upload mixed manuscript artifacts, resolve references against canonical sources, and let editors approve
            citation repairs with evidence.
          </p>
        </div>
      </section>
      <SummaryCards citationCase={demoCase} />
      <section className="twoColumn">
        <UploadPanel />
        <div className="card">
          <div className="sectionHeader">
            <h2>Authority Stack</h2>
            <p className="muted">`Crossref` and `OpenAlex` form the default source-of-truth layer for paper identity.</p>
          </div>
          <ul className="list">
            <li>Deterministic parsers handle `LaTeX`, `.bib`, `Docx`, and baseline `PDF` text extraction.</li>
            <li>Rules-first contribution labels keep the reviewer workflow transparent and auditable.</li>
            <li>Local background jobs handle OCR fallback, reranking, and ambiguous cases when extra processing is needed.</li>
          </ul>
        </div>
      </section>
      <section className="twoColumn">
        <ReviewWorkbench citationCase={demoCase} />
        <ExportPanel />
      </section>
      <CitationReviewTable citationCase={demoCase} />
    </main>
  );
}
