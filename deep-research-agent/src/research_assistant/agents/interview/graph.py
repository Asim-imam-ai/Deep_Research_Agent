"""Compile independent interview graph; no double fan-in or duplicate search calls."""

from langgraph.graph import END, START, StateGraph

from research_assistant.agents.interview.edges import route_after_answer
from research_assistant.agents.interview.nodes import (
    generate_answer,
    generate_question,
    generate_search_query,
    save_interview,
    search_web,
)
from research_assistant.agents.interview.state import InterviewState


def build_interview_graph():
    builder = StateGraph(InterviewState)
    builder.add_node("ask_question", generate_question)
    builder.add_node("make_query", generate_search_query)
    builder.add_node("search_web", search_web)
    builder.add_node("answer_question", generate_answer)
    builder.add_node("save_interview", save_interview)
    builder.add_edge(START, "ask_question")
    builder.add_edge("ask_question", "make_query")
    builder.add_edge("make_query", "search_web")
    builder.add_edge("search_web", "answer_question")
    builder.add_conditional_edges("answer_question", route_after_answer)
    builder.add_edge("save_interview", END)
    return builder.compile()


graph = build_interview_graph()
