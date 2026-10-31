"""SQLAlchemy engine factory."""

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from research_assistant.core.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)
