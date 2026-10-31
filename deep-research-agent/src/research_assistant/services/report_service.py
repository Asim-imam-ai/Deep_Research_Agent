"""Report graph API and durable report lookup."""

from uuid import UUID

from sqlalchemy.orm import Session

from research_assistant.agents.report.graph import graph
from research_assistant.agents.research.schemas import ResearchSection
from research_assistant.infrastructure.persistence.report_repository import ReportRepository


def write_report(topic: str, sections: list[ResearchSection]):
    return graph.invoke({"topic": topic, "sections": sections})["report"]


class ReportManagementService:
    def get(self, db: Session, report_id: UUID):
        return ReportRepository(db).get(report_id)
