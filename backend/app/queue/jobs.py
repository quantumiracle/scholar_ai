from __future__ import annotations

from dataclasses import asdict, dataclass

from app.schemas.citation import SourceAsset


@dataclass(slots=True)
class QueuedJob:
    job_type: str
    payload: dict
    preferred_runtime: str = "cpu"


class MlxJobPlanner:
    def plan_pdf_fallback_jobs(self, asset: SourceAsset) -> list[dict]:
        return [
            asdict(
                QueuedJob(
                job_type="pdf_layout_fallback",
                payload={"filename": asset.filename, "format": asset.format.value},
                preferred_runtime="mlx-gpu",
                )
            )
        ]

    def plan_ambiguous_resolution_job(self, mention_id: str, reference_title: str) -> dict:
        return asdict(
            QueuedJob(
                job_type="citation_rerank",
                payload={"mention_id": mention_id, "reference_title": reference_title},
                preferred_runtime="mlx-gpu",
            )
        )
