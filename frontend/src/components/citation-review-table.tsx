import { CitationCase } from "@/lib/types";

export function CitationReviewTable({ citationCase }: { citationCase: CitationCase }) {
  return (
    <div className="card">
      <div className="sectionHeader">
        <h2>Citation Review Queue</h2>
        <p className="muted">Inspect confidence, contribution labels, and manual relinking candidates.</p>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Mention</th>
            <th>Contribution</th>
            <th>Confidence</th>
            <th>Canonical Paper</th>
            <th>Rationale</th>
          </tr>
        </thead>
        <tbody>
          {citationCase.decisions.map((decision) => (
            <tr key={decision.mention_id}>
              <td>{decision.mention_id}</td>
              <td>{decision.contribution_type}</td>
              <td>{decision.confidence.toFixed(2)}</td>
              <td>{decision.canonical_paper_id ?? "Needs resolution"}</td>
              <td>{decision.rationale ?? "Awaiting review"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
