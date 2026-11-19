"""LangGraph workflow – wires the agents into a directed graph with a feedback loop."""

import os
from typing import TypedDict

from langgraph.graph import END, StateGraph

from .agents.planner import planner_node
from .agents.researcher import dedup_node, research_node, summarize_node
from .agents.reviewer import reviewer_node
from .agents.writer import writer_node
from .config import settings
from .export.pdf import markdown_to_pdf


class ResearchState(TypedDict, total=False):
    job_id: str
    topic: str
    title: str
    plan: list
    raw_results: list
    sources: list
    duplicates_removed: int
    notes: dict
    draft: str
    review: dict
    revisions: int
    report: str
    md_path: str
    pdf_path: str
    stage: str


def export_node(state: ResearchState) -> dict:
    """Build the final report with an IEEE-style References section and export."""
    refs = "\n\n".join(
        f"[{s['id']}] {s['title']}, {s['url']}" for s in state["sources"]
    )
    report = f"{state['draft'].rstrip()}\n\n## REFERENCES\n\n{refs}\n"

    out_dir = os.path.join(settings.output_dir, state["job_id"])
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, "report.md")
    pdf_path = os.path.join(out_dir, "report.pdf")

    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(report)
    markdown_to_pdf(report, pdf_path)

    return {
        "report": report,
        "md_path": md_path,
        "pdf_path": pdf_path,
        "stage": "completed",
    }


def _after_review(state: ResearchState) -> str:
    """Feedback loop: re-write until approved or revision cap hit."""
    if state["review"].get("approved") or state.get("revisions", 0) >= settings.max_revisions:
        return "export"
    return "writer"


def build_graph() -> StateGraph:
    g = StateGraph(ResearchState)

    g.add_node("planner", planner_node)
    g.add_node("researcher", research_node)
    g.add_node("dedup", dedup_node)
    g.add_node("summariser", summarize_node)
    g.add_node("writer", writer_node)
    g.add_node("reviewer", reviewer_node)
    g.add_node("export", export_node)

    g.set_entry_point("planner")
    g.add_edge("planner", "researcher")
    g.add_edge("researcher", "dedup")
    g.add_edge("dedup", "summariser")
    g.add_edge("summariser", "writer")
    g.add_edge("writer", "reviewer")
    g.add_conditional_edges(
        "reviewer", _after_review, {"writer": "writer", "export": "export"}
    )
    g.add_edge("export", END)

    return g.compile()


graph = build_graph()
