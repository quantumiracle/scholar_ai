import { CitationCase } from "@/lib/types";

export function SummaryCards({ citationCase }: { citationCase: CitationCase }) {
  const resolved = citationCase.decisions.filter((item) => item.canonical_paper_id).length;

  const cards = [
    { label: "References", value: citationCase.manuscript.references.length },
    { label: "Citation Mentions", value: citationCase.manuscript.citations.length },
    { label: "Resolved Links", value: resolved },
    { label: "Canonical Papers", value: citationCase.canonical_papers.length }
  ];

  return (
    <div className="grid">
      {cards.map((card) => (
        <div className="card" key={card.label}>
          <p className="muted">{card.label}</p>
          <h3>{card.value}</h3>
        </div>
      ))}
    </div>
  );
}
