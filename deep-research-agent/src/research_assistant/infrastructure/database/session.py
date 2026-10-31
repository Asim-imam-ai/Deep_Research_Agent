"""Unit-of-work session helpers."""

from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker

from research_assistant.infrastructure.database.connection import get_engine


def session_factory():
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


@contextmanager
def session_scope():
    with session_factory()() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
