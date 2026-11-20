"""Research Agent – search, de-duplicate, and summarise per task."""

from ..config import settings
from ..llm import chat
from ..tools.dedup import deduplicate
from ..tools.search import web_search


def research_node(state: dict) -> dict:
    """Execute every search query in the plan; tag results with their task id."""
    raw: list[dict] = []
    for task in state["plan"]:
        for query in task["search_queries"]:
            try:
                for result in web_search(query):
                    result["task_id"] = task["id"]
                    raw.append(result)
            except Exception as exc:
                print(f"[search failed] {query}: {exc}")
    if not raw:
        raise RuntimeError("No search results returned – check TAVILY_API_KEY.")
    return {"raw_results": raw, "stage": "searching"}


def dedup_node(state: dict) -> dict:
    sources, removed = deduplicate(state["raw_results"], settings.dedup_threshold)
    for idx, src in enumerate(sources, start=1):
        src["id"] = idx
    return {"sources": sources, "duplicates_removed": removed, "stage": "deduplicating"}


SUMMARY_SYSTEM = """\
You are a research analyst.  Using ONLY the numbered sources provided, write
concise notes (bullet points) answering the research question.
Cite every fact with its source number like [3].  Never invent facts or citations."""


def summarize_node(state: dict) -> dict:
    notes: dict[int, str] = {}
    for task in state["plan"]:
        srcs = [s for s in state["sources"] if s["task_id"] == task["id"]]
        if not srcs:
            notes[task["id"]] = "_No sources found for this question._"
            continue
        block = "\n\n".join(f"[{s['id']}] {s['title']}\n{s['content']}" for s in srcs)
        try:
            notes[task["id"]] = chat(
                SUMMARY_SYSTEM,
                f"Question: {task['question']}\n\nSources:\n{block}",
                max_tokens=1500,
            )
        except Exception as exc:
            # Fallback when LLM is unavailable
            notes[task["id"]] = f"_Summary unavailable: {exc}_"
    return {"notes": notes, "stage": "summarising"}
