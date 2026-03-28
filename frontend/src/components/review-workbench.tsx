"use client";

import { useMemo, useState } from "react";

import { CitationCase } from "@/lib/types";

type ReviewState = Record<
  string,
  {
    status: "approved" | "needs_human";
    canonical_paper_id: string;
  }
>;

export function ReviewWorkbench({ citationCase }: { citationCase: CitationCase }) {
  const [reviewState, setReviewState] = useState<ReviewState>(() =>
    Object.fromEntries(
      citationCase.decisions.map((decision) => [
        decision.mention_id,
        {
          status: decision.canonical_paper_id ? "approved" : "needs_human",
          canonical_paper_id: decision.canonical_paper_id ?? ""
        }
      ])
    )
  );

  const readyToExport = useMemo(
    () => Object.values(reviewState).every((item) => item.status === "approved"),
    [reviewState]
  );

  return (
    <div className="card">
      <div className="sectionHeader">
        <h2>Reviewer Actions</h2>
        <p className="muted">Approve good matches, flag ambiguous ones, or manually relink to a canonical paper.</p>
      </div>
      <div className="stack">
        {citationCase.decisions.map((decision) => (
          <div className="reviewRow" key={decision.mention_id}>
            <div>
              <strong>{decision.mention_id}</strong>
              <p className="muted">{decision.rationale ?? "No rationale available."}</p>
            </div>
            <select
              className="input"
              value={reviewState[decision.mention_id]?.canonical_paper_id ?? ""}
              onChange={(event) =>
                setReviewState((current) => ({
                  ...current,
                  [decision.mention_id]: {
                    status: event.target.value ? "approved" : "needs_human",
                    canonical_paper_id: event.target.value
                  }
                }))
              }
            >
              <option value="">Needs manual selection</option>
              {citationCase.canonical_papers.map((paper) => (
                <option key={paper.paper_id} value={paper.paper_id}>
                  {paper.title}
                </option>
              ))}
            </select>
            <button
              className="button secondary"
              type="button"
              onClick={() =>
                setReviewState((current) => ({
                  ...current,
                  [decision.mention_id]: {
                    ...current[decision.mention_id],
                    status: current[decision.mention_id]?.status === "approved" ? "needs_human" : "approved"
                  }
                }))
              }
            >
              {reviewState[decision.mention_id]?.status === "approved" ? "Mark Needs Human" : "Approve"}
            </button>
          </div>
        ))}
      </div>
      <div className="exportBanner">
        <strong>{readyToExport ? "All citations are ready for export." : "Some citations still require review."}</strong>
      </div>
    </div>
  );
}
