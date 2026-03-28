# Output Schema

The export bundle contains four top-level outputs:

## `json_document`

- `manuscript`: normalized manuscript representation
- `canonical_papers`: canonical records chosen during resolution
- `decisions`: contribution and linking decisions per mention
- `graph`: citation graph snapshot with nodes, edges, and metrics

## `bibtex`

A corrected bibliography export built from canonical paper metadata.

## `report_markdown`

A reviewer-facing summary with unresolved mentions and counts.

## `graph_snapshot`

Structured graph output suitable for indexing, analytics, and downstream
reconciliation.
