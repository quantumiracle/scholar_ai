# MLX Worker Notes

Use MLX workers only for jobs that materially benefit from GPU acceleration:

- OCR-heavy PDF parsing fallback
- Embedding generation for candidate retrieval
- Citation candidate reranking
- Ambiguous contribution classification

The backend exposes command-building helpers in `backend/app/workers/mlx.py`.

Example launch shape:

```bash
NO_COLOR=1 TERM=dumb mlx worker launch \
  --resourcetype public-arnold \
  --cluster cloudnative-lf \
  --queuename compute-3291-lf-cloudnative-ai-workspace.public-guarantee \
  --gpu 1 \
  --type NVIDIA-H20 -- \
  bash -lc "python backend/app/workers/run_job.py"
```

Keep deterministic parsing and authority resolution on CPU to avoid unnecessary
queue latency.
