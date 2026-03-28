# Architecture

The system is split into an upload-and-review frontend and a backend orchestration
layer.

## Flow

1. A reviewer uploads mixed manuscript assets.
2. The ingestion service runs deterministic parsing by format.
3. Bibliography entries are normalized into canonical reference records.
4. `Crossref` and `OpenAlex` are queried for paper identity resolution.
5. The contribution classifier labels each citation by technical role.
6. The graph service builds nodes and edges for manuscripts, papers, and authors.
7. The reviewer approves or edits decisions, then exports structured artifacts.

## Runtime Separation

- CPU path: API, deterministic parsing, authority lookups, review workflow
- MLX/GPU path: PDF OCR fallback, dense retrieval, candidate reranking, ambiguous citation classification
