export function ExportPanel() {
  const outputs = [
    "Corrected BibTeX",
    "Structured citation JSON",
    "Reviewer report markdown",
    "Citation graph snapshot"
  ];

  return (
    <div className="card">
      <div className="sectionHeader">
        <h2>Export Targets</h2>
        <p className="muted">Approved cases emit artifacts for indexing, audit, and downstream reconciliation.</p>
      </div>
      <ul className="list">
        {outputs.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <button className="button" type="button">
        Prepare Export Bundle
      </button>
    </div>
  );
}
