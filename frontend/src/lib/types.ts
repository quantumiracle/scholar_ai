export type ContributionType =
  | "baseline_method"
  | "dataset_benchmark"
  | "model_architecture"
  | "theorem_proof"
  | "implementation_tooling"
  | "negative_comparison"
  | "background_survey"
  | "supporting_evidence"
  | "unknown";

export interface CitationDecision {
  mention_id: string;
  reference_id?: string | null;
  canonical_paper_id?: string | null;
  contribution_type: ContributionType;
  confidence: number;
  rationale?: string | null;
}

export interface CanonicalPaper {
  paper_id: string;
  title: string;
  doi?: string | null;
  year?: number | null;
  venue?: string | null;
}

export interface CitationCase {
  manuscript: {
    manuscript_id: string;
    title?: string | null;
    citations: Array<{ mention_id: string; marker: string; context: string }>;
    references: Array<{ reference_id: string; title?: string | null; doi?: string | null }>;
  };
  canonical_papers: CanonicalPaper[];
  decisions: CitationDecision[];
}
