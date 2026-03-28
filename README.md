# Paper Reference Refactor System

This repository contains a greenfield implementation of a citation review system
for research manuscripts. The system ingests mixed paper assets, resolves
references to canonical paper identities, classifies each citation by technical
contribution, and produces reviewable exports for downstream indexing.

## Repository Layout

- `backend/`: FastAPI-oriented backend, domain schemas, parsing and resolution services
- `frontend/`: Next.js reviewer UI scaffold
- `docs/`: architecture and output schema documentation
- `ops/`: local runtime notes and operational helpers

## MVP Scope

- Mixed input ingestion: `LaTeX`, `BibTeX`, `Docx`, `PDF`, and metadata exports
- Canonical citation graph construction
- `Crossref` and `OpenAlex` provider integration
- Rules-first contribution classification with local background job hooks for heavier parsing or reranking
- Reviewer workflow for approving or correcting citation decisions
- Structured exports for clean indexing and impact reconciliation
