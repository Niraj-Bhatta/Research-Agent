"""Web search via Tavily API."""

from tavily import TavilyClient

from ..config import settings


def web_search(query: str, max_results: int | None = None) -> list[dict]:
    """Return [{title, url, content, query}] for a Tavily search."""
    client = TavilyClient(api_key=settings.tavily_api_key)
    resp = client.search(
        query=query,
        max_results=max_results or settings.results_per_query,
        search_depth="advanced",
    )
    return [
        {
            "title": r.get("title") or r["url"],
            "url": r["url"],
            "content": r.get("content", ""),
            "query": query,
        }
        for r in resp.get("results", [])
        if r.get("content")
    ]
