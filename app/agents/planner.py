"""Planner Agent – turns a topic into a structured research plan."""

from ..llm import chat_json

SYSTEM = """\
You are a Research Planner.  Break the user's topic into 4-6 focused research
tasks that together cover the topic comprehensively (background, current state,
key players, challenges, future outlook, etc.).

Return JSON:
{
  "title": "<report title>",
  "tasks": [
    {"id": 1, "question": "...", "search_queries": ["...", "..."]}
  ]
}
Provide exactly 2 search queries per task."""


def planner_node(state: dict) -> dict:
    plan = chat_json(SYSTEM, f"Topic: {state['topic']}")
    return {"title": plan["title"], "plan": plan["tasks"], "stage": "planning"}
