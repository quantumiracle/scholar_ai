from __future__ import annotations

from dataclasses import dataclass, field

from app.schemas.citation import CitationReviewCase
from app.schemas.graph import CitationGraphSnapshot, ExportBundle, IndexRecord
from app.schemas.review import ReviewAction


@dataclass
class InMemoryRepository:
    cases: dict[str, CitationReviewCase] = field(default_factory=dict)
    graphs: dict[str, CitationGraphSnapshot] = field(default_factory=dict)
    exports: dict[str, ExportBundle] = field(default_factory=dict)
    index_records: dict[str, list[IndexRecord]] = field(default_factory=dict)
    review_actions: list[ReviewAction] = field(default_factory=list)

    def save_case(self, case: CitationReviewCase) -> CitationReviewCase:
        self.cases[case.manuscript.manuscript_id] = case
        return case

    def get_case(self, manuscript_id: str) -> CitationReviewCase | None:
        return self.cases.get(manuscript_id)

    def list_cases(self) -> list[CitationReviewCase]:
        return list(self.cases.values())

    def add_review_action(self, action: ReviewAction) -> ReviewAction:
        self.review_actions.append(action)
        return action

    def save_graph(self, manuscript_id: str, graph: CitationGraphSnapshot) -> CitationGraphSnapshot:
        self.graphs[manuscript_id] = graph
        return graph

    def get_graph(self, manuscript_id: str) -> CitationGraphSnapshot | None:
        return self.graphs.get(manuscript_id)

    def save_export(self, manuscript_id: str, bundle: ExportBundle) -> ExportBundle:
        self.exports[manuscript_id] = bundle
        return bundle

    def get_export(self, manuscript_id: str) -> ExportBundle | None:
        return self.exports.get(manuscript_id)

    def save_index_records(self, manuscript_id: str, records: list[IndexRecord]) -> list[IndexRecord]:
        self.index_records[manuscript_id] = records
        return records

    def get_index_records(self, manuscript_id: str) -> list[IndexRecord]:
        return self.index_records.get(manuscript_id, [])
