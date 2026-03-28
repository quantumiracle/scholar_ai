"use client";

import { useState } from "react";

export function UploadPanel() {
  const [message, setMessage] = useState("Drag in LaTeX, BibTeX, PDF, Docx, or metadata exports.");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("Frontend scaffold ready. Wire this form to `/api/ingest` after installing dependencies.");
  }

  return (
    <div className="card">
      <div className="sectionHeader">
        <h2>Upload Manuscript Assets</h2>
        <p className="muted">The MVP API accepts mixed assets and normalizes them into one review case.</p>
      </div>
      <form onSubmit={handleSubmit} className="stack">
        <input className="input" name="title" placeholder="Manuscript title" />
        <textarea
          className="input textarea"
          name="notes"
          placeholder="Paste abstract, notes, or import metadata here."
        />
        <button className="button" type="submit">
          Prepare Ingestion Request
        </button>
      </form>
      <p className="muted">{message}</p>
    </div>
  );
}
