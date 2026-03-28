# Local Run Notes

This repository is designed to run locally on a single machine.

## Recommended Split

- Foreground web/API processes:
  - FastAPI backend
  - Next.js frontend
- Local background jobs:
  - PDF fallback extraction
  - Citation reranking
  - Ambiguous contribution classification

## Example Commands

```bash
python3 -m uvicorn app.main:app --app-dir backend --host :: --port 8000
```

```bash
npm run dev -- --hostname :: --port 3000
```

Keep extra processing local unless the repository later adds a different remote
execution backend on purpose.
