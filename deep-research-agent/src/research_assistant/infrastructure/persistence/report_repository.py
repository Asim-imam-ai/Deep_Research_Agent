"""Idempotent persistence for research reports, analysts, interviews, and sources."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from research_assistant.agents.report.schemas import ReportOutput
from research_assistant.infrastructure.database.models import (
    AnalystRecord,
    InterviewRecord,
    Report,
    SourceRecord,
)
from research_assistant.schemas.analyst import Analyst


class ReportRepository:
    """Persist completed research results using SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, report_id: UUID):
        """Retrieve a saved report by its ID."""
        return self.db.get(Report, report_id)

    def save(self, run_id: UUID, report: ReportOutput) -> Report:
        """Save or update a report and its associated records.

        Convert Pydantic URL objects to strings before inserting
        them into PostgreSQL.
        """
        report = ReportOutput.model_validate(report)

        previous = self.db.scalar(select(Report).where(Report.run_id == run_id))

        report_data = report.model_dump(mode="json")

        if previous is not None:
            previous.title = report.title
            previous.markdown = report.markdown
            previous.data = report_data
            record = previous
        else:
            record = Report(
                run_id=run_id,
                title=report.title,
                markdown=report.markdown,
                data=report_data,
            )
            self.db.add(record)

        # Replace associated records when a report is saved again.
        for model in (
            AnalystRecord,
            InterviewRecord,
            SourceRecord,
        ):
            self.db.execute(delete(model).where(model.run_id == run_id))

        seen_analysts: set[str] = set()
        seen_urls: set[str] = set()

        for position, section in enumerate(report.sections):
            analyst = Analyst.model_validate(section.analyst)

            self.db.add(
                AnalystRecord(
                    run_id=run_id,
                    position=position,
                    data=analyst.model_dump(mode="json"),
                )
            )

            if analyst.name not in seen_analysts:
                self.db.add(
                    InterviewRecord(
                        run_id=run_id,
                        analyst_name=analyst.name,
                        transcript=section.transcript,
                    )
                )
                seen_analysts.add(analyst.name)

            for source in section.sources:
                # Pydantic HttpUrl is not a PostgreSQL string.
                # Always convert it before database insertion.
                url = str(source.url)

                if url in seen_urls:
                    continue

                self.db.add(
                    SourceRecord(
                        run_id=run_id,
                        url=url,
                        title=source.title,
                    )
                )
                seen_urls.add(url)

        # Raise database errors before returning to the worker.
        # The enclosing session_scope handles the transaction.
        self.db.flush()

        return record
