"""Database-backed polling worker for durable research execution.

Run as a separate process, not as a FastAPI background task.
"""

import logging
import threading
import time
from uuid import UUID, uuid4

from langgraph.types import Command

from research_assistant.agents.report.schemas import ReportOutput
from research_assistant.core.config import get_settings
from research_assistant.guardrails.output_validation import (
    ReportValidationError,
    validate_report,
)
from research_assistant.infrastructure.checkpoint.factory import persistent_graph
from research_assistant.infrastructure.checkpoint.postgres import postgres_checkpointer
from research_assistant.infrastructure.database.models import RunStatus
from research_assistant.infrastructure.database.repositories import RunRepository
from research_assistant.infrastructure.database.session import session_scope
from research_assistant.infrastructure.persistence.report_repository import ReportRepository
from research_assistant.observability.metrics import increment, measure
from research_assistant.observability.tracing import configure_tracing, trace_config
from research_assistant.schemas.analyst import Analyst

logger = logging.getLogger(__name__)

NODE_EVENTS = {
    "generate_analysts": "analysts_generated",
    "conduct_research": "interview_completed",
    "create_report": "report_generating",
}


def event(
    run_id: UUID,
    kind: str,
    payload: dict | None = None,
) -> None:
    """Persist a research workflow event."""
    with session_scope() as db:
        RunRepository(db).event(run_id, kind, payload)


def keep_lease(
    run_id: UUID,
    worker_id: str,
    stop: threading.Event,
) -> None:
    """Periodically renew the worker lease."""
    settings = get_settings()

    while not stop.wait(settings.worker_heartbeat_seconds):
        try:
            with session_scope() as db:
                renewed = RunRepository(db).heartbeat(
                    run_id,
                    worker_id,
                    settings.worker_lease_seconds,
                )

            if not renewed:
                logger.error(
                    "Worker %s lost lease for research run %s",
                    worker_id,
                    run_id,
                )
                return

        except Exception:
            logger.exception(
                "Failed to renew lease for research run %s",
                run_id,
            )
            return


def persist_final(
    run_id: UUID,
    worker_id: str,
    values: dict,
) -> None:
    """Validate and persist a completed research report."""
    if "report" not in values:
        raise ReportValidationError("Graph completed without a final report")

    try:
        report = ReportOutput.model_validate(values["report"])
    except ValueError as exc:
        raise ReportValidationError("Graph produced an invalid report schema") from exc

    report = validate_report(
        report,
        require_sources=get_settings().enforce_report_sources,
    )

    with session_scope() as db:
        repo = RunRepository(db)
        run = repo.get(run_id, lock=True)

        if run is None:
            raise RuntimeError("Research run no longer exists")

        if run.worker_id != worker_id:
            raise RuntimeError("Worker lease lost before report completion")

        saved = ReportRepository(db).save(run_id, report)

        repo.finish(
            run_id,
            RunStatus.completed,
            worker_id,
        )

        repo.event(
            run_id,
            "research_completed",
            {"report_id": str(saved.id)},
        )

    logger.info(
        "Research run %s completed successfully; report_id=%s",
        run_id,
        saved.id,
    )


def _await_feedback(
    run_id: UUID,
    worker_id: str,
    values: dict,
) -> None:
    """Persist the analyst approval state."""
    analysts = [
        Analyst.model_validate(item).model_dump(mode="json") for item in values.get("analysts", [])
    ]

    with session_scope() as db:
        repo = RunRepository(db)

        run = repo.get(run_id, lock=True)

        if run is None or run.worker_id != worker_id:
            raise RuntimeError("Worker lease lost before saving analyst feedback state")

        repo.finish(
            run_id,
            RunStatus.awaiting_feedback,
            worker_id,
        )

        repo.event(
            run_id,
            "awaiting_human_feedback",
            {"analysts": analysts},
        )

    logger.info(
        "Research run %s awaiting human feedback",
        run_id,
    )


def handle_failure(
    run_id: UUID,
    worker_id: str,
    exc: Exception,
) -> None:
    """Persist a research failure and apply retry policy."""
    increment("research.failures")

    logger.error(
        "Research run %s failed: %s",
        run_id,
        exc,
    )

    # Invalid completed reports should not be retried
    # from the same finished LangGraph checkpoint.
    retryable = not isinstance(exc, ReportValidationError)

    with session_scope() as db:
        repo = RunRepository(db)
        run = repo.get(run_id, lock=True)

        if run is None:
            logger.warning(
                "Cannot record failure: run %s not found",
                run_id,
            )
            return

        if run.worker_id != worker_id:
            logger.warning(
                "Cannot record failure: lease lost for run %s",
                run_id,
            )
            return

        run.error = str(exc)[:2000]

        attempts = run.attempts
        max_attempts = get_settings().max_worker_attempts

        if retryable and attempts < max_attempts:
            repo.finish(
                run_id,
                RunStatus.queued,
                worker_id,
            )

            repo.event(
                run_id,
                "research_retrying",
                {
                    "attempt": attempts,
                    "max_attempts": max_attempts,
                },
            )

            logger.warning(
                "Research run %s requeued after attempt %s/%s",
                run_id,
                attempts,
                max_attempts,
            )

        else:
            repo.finish(
                run_id,
                RunStatus.failed,
                worker_id,
            )

            repo.event(
                run_id,
                "research_failed",
                {
                    "error": str(exc)[:500],
                    "retryable": False,
                },
            )

            logger.error(
                "Research run %s marked as failed",
                run_id,
            )


def execute(
    run_id: UUID,
    worker_id: str,
) -> None:
    """Execute or resume a research workflow."""
    stop = threading.Event()

    heartbeat = threading.Thread(
        target=keep_lease,
        args=(run_id, worker_id, stop),
        daemon=True,
        name=f"research-heartbeat-{run_id}",
    )
    heartbeat.start()

    try:
        with session_scope() as db:
            run = RunRepository(db).get(run_id)

            if run is None:
                logger.warning(
                    "Research run %s was not found",
                    run_id,
                )
                return

            feedback = run.pending_feedback

            if feedback is not None:
                run.pending_feedback = None

            topic = run.topic
            n_analysts = run.max_analysts
            turns = run.max_num_turns

        config = {
            "configurable": {
                "thread_id": str(run_id),
            },
            **trace_config(run_id),
        }

        with postgres_checkpointer() as saver:
            graph = persistent_graph(saver)
            snapshot = graph.get_state(config)

            if feedback is not None:
                graph_input = Command(resume=feedback)

                event(
                    run_id,
                    "research_resumed",
                    {"approved": feedback["approved"]},
                )

                logger.info(
                    "Resuming research run %s with human feedback",
                    run_id,
                )

            elif snapshot.values:
                # A finished graph may have a completed report
                # that was not persisted before a worker crash.
                if not snapshot.next and "report" in snapshot.values:
                    logger.info(
                        "Recovering completed run %s from checkpoint",
                        run_id,
                    )

                    persist_final(
                        run_id,
                        worker_id,
                        snapshot.values,
                    )
                    return

                # A human-interrupted graph must await feedback;
                # passing None here could otherwise leave it stuck.
                if snapshot.interrupts:
                    _await_feedback(
                        run_id,
                        worker_id,
                        snapshot.values,
                    )
                    return

                graph_input = None

                logger.info(
                    "Resuming research run %s from checkpoint",
                    run_id,
                )

            else:
                graph_input = {
                    "topic": topic,
                    "max_analysts": n_analysts,
                    "max_num_turns": turns,
                    "sections": [],
                }

                logger.info(
                    "Starting research run %s: %s",
                    run_id,
                    topic,
                )

            with measure("research.graph_execution"):
                updates = graph.stream(
                    graph_input,
                    config=config,
                    stream_mode="updates",
                )

                for update in updates:
                    for node in update:
                        if node == "__interrupt__":
                            continue

                        event_kind = NODE_EVENTS.get(node)

                        if event_kind is not None:
                            event(
                                run_id,
                                event_kind,
                                {"node": node},
                            )

                            logger.info(
                                "Research run %s completed node %s",
                                run_id,
                                node,
                            )

            snapshot = graph.get_state(config)

            if snapshot.interrupts:
                _await_feedback(
                    run_id,
                    worker_id,
                    snapshot.values,
                )
                return

            if not snapshot.values or "report" not in snapshot.values:
                raise ReportValidationError("Graph ended without a final report")

            persist_final(
                run_id,
                worker_id,
                snapshot.values,
            )

    except Exception as exc:
        # Job failures must be recorded without killing
        # the entire long-running polling worker.
        logger.exception(
            "Research execution failed for run %s",
            run_id,
        )

        handle_failure(
            run_id,
            worker_id,
            exc,
        )

    finally:
        stop.set()
        heartbeat.join(timeout=2)


def run_forever() -> None:
    """Poll for queued research runs and execute them."""
    settings = get_settings()
    worker_id = str(uuid4())

    configure_tracing()

    logger.info(
        "Research worker started: %s",
        worker_id,
    )

    try:
        while True:
            try:
                with session_scope() as db:
                    run = RunRepository(db).claim(
                        worker_id,
                        settings.worker_lease_seconds,
                    )

                    run_id = run.id if run else None

                if run_id is not None:
                    execute(
                        run_id,
                        worker_id,
                    )
                else:
                    time.sleep(settings.worker_poll_seconds)

            except Exception:
                # A polling/database failure should be logged,
                # then the worker should try again later.
                logger.exception("Worker polling failed")

                time.sleep(settings.worker_poll_seconds)

    except KeyboardInterrupt:
        logger.info("Research worker shutting down")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
    )

    run_forever()
