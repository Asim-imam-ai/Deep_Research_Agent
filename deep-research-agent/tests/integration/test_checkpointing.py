"""Checkpoint test requires a separate disposable PostgreSQL database."""

import os
from typing import TypedDict

import pytest
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    count: int


def increment(state: State):
    return {"count": state["count"] + 1}


@pytest.mark.skipif(
    not os.getenv("TEST_CHECKPOINT_DATABASE_URL"), reason="Set TEST_CHECKPOINT_DATABASE_URL"
)
def test_postgres_checkpoint_survives_reconnect():
    url = os.environ["TEST_CHECKPOINT_DATABASE_URL"]
    from uuid import uuid4

    config = {"configurable": {"thread_id": str(uuid4())}}
    builder = StateGraph(State)
    builder.add_node("increment", increment)
    builder.add_edge(START, "increment")
    builder.add_edge("increment", END)
    with PostgresSaver.from_conn_string(url) as saver:
        saver.setup()
        graph = builder.compile(checkpointer=saver)
        assert graph.invoke({"count": 3}, config)["count"] == 4
    with PostgresSaver.from_conn_string(url) as saver:
        graph = builder.compile(checkpointer=saver)
        assert graph.get_state(config).values["count"] == 4
