from __future__ import annotations

from dataclasses import asdict
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.repository import InMemoryRepository
from app.schemas.citation import DocumentFormat, SourceAsset, to_dict
from app.schemas.review import IngestRequest, ReviewAction, ReviewStatus
from app.services.ingest.service import IngestionService


def build_router(repository: InMemoryRepository | None = None) -> APIRouter:
    router = APIRouter(prefix="/api")
    store = repository or InMemoryRepository()
    ingestion = IngestionService()

    @router.get("/health")
    def healthcheck():
        return {"status": "ok"}

    @router.get("/cases")
    def list_cases():
        return [to_dict(case) for case in store.list_cases()]

    @router.get("/cases/{manuscript_id}")
    def get_case(manuscript_id: str):
        case = store.get_case(manuscript_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return to_dict(case)

    @router.get("/cases/{manuscript_id}/graph")
    def get_graph(manuscript_id: str):
        graph = store.get_graph(manuscript_id)
        if not graph:
            raise HTTPException(status_code=404, detail="Graph not found")
        return to_dict(graph)

    @router.get("/cases/{manuscript_id}/export")
    def get_export(manuscript_id: str):
        bundle = store.get_export(manuscript_id)
        if not bundle:
            raise HTTPException(status_code=404, detail="Export bundle not found")
        return {
            "json": bundle.json_document,
            "bibtex": bundle.bibtex,
            "report_markdown": bundle.report_markdown,
            "graph": to_dict(bundle.graph_snapshot),
        }

    @router.get("/cases/{manuscript_id}/index-records")
    def get_index_records(manuscript_id: str):
        return [to_dict(record) for record in store.get_index_records(manuscript_id)]

    @router.post("/ingest")
    def ingest_case(payload: dict):
        assets = [
            SourceAsset(
                filename=asset["filename"],
                content=asset["content"],
                format=DocumentFormat(asset["format"]),
                media_type=asset.get("media_type"),
            )
            for asset in payload.get("assets", [])
        ]
        request = IngestRequest(
            manuscript_id=payload["manuscript_id"],
            title=payload.get("title"),
            assets=assets,
            metadata=payload.get("metadata", {}),
        )
        response = ingestion.ingest(request)
        store.save_case(response.case)
        bundle = ingestion.export(response.case)
        store.save_graph(request.manuscript_id, bundle.graph_snapshot)
        store.save_export(request.manuscript_id, bundle)
        store.save_index_records(
            request.manuscript_id,
            ingestion.graph_service.build_index_records(response.case),
        )
        return {
            "case": to_dict(response.case),
            "warnings": response.warnings,
            "queued_jobs": response.queued_jobs,
            "exports": {
                "json": bundle.json_document,
                "bibtex": bundle.bibtex,
                "report_markdown": bundle.report_markdown,
            },
        }

    @router.post("/cases/{manuscript_id}/review")
    def record_review(manuscript_id: str, payload: dict):
        case = store.get_case(manuscript_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        action = ReviewAction(
            action_id=str(uuid4()),
            manuscript_id=manuscript_id,
            citation_id=payload["citation_id"],
            actor=payload.get("actor", "reviewer"),
            status=ReviewStatus(payload.get("status", ReviewStatus.APPROVED.value)),
            note=payload.get("note"),
            chosen_paper_id=payload.get("chosen_paper_id"),
            chosen_label=payload.get("chosen_label"),
        )
        store.add_review_action(action)
        return asdict(action)

    return router
