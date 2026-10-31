"""Persistent LangGraph saver. Only the parent graph owns a checkpointer."""

from contextlib import contextmanager

from langgraph.checkpoint.postgres import PostgresSaver

from research_assistant.core.config import get_settings


@contextmanager
def postgres_checkpointer():
    with PostgresSaver.from_conn_string(get_settings().checkpoint_database_url) as saver:
        yield saver


def setup_checkpointer():
    with postgres_checkpointer() as saver:
        saver.setup()
