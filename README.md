# Paper Reference Refactor System

This repository contains a greenfield implementation of a citation review system
for research manuscripts. The system ingests mixed paper assets, resolves
references to canonical paper identities, classifies each citation by technical
contribution, and produces reviewable exports for downstream indexing.

## Repository Layout

- `backend/`: FastAPI-oriented backend, domain schemas, parsing and resolution services
- `frontend/`: Next.js reviewer UI scaffold
- `docs/`: architecture and output schema documentation
- `ops/mlx/`: MLX worker notes and starter scripts for GPU-backed jobs

## MVP Scope

- Mixed input ingestion: `LaTeX`, `BibTeX`, `Docx`, `PDF`, and metadata exports
- Canonical citation graph construction
- `Crossref` and `OpenAlex` provider integration
- Rules-first contribution classification with MLX job hooks for heavier models
- Reviewer workflow for approving or correcting citation decisions
- Structured exports for clean indexing and impact reconciliation
