"""Duplicate detection: exact URL de-dup + TF-IDF cosine similarity."""

from urllib.parse import urlparse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _normalise_url(url: str) -> str:
    p = urlparse(url)
    return (p.netloc.lower().removeprefix("www.") + p.path.rstrip("/")).lower()


def deduplicate(
    items: list[dict], threshold: float = 0.85
) -> tuple[list[dict], int]:
    """Drop items with a repeated URL or content ≥ threshold similarity."""
    seen_urls: set[str] = set()
    unique: list[dict] = []
    for item in items:
        key = _normalise_url(item["url"])
        if key not in seen_urls:
            seen_urls.add(key)
            unique.append(item)

    if len(unique) < 2:
        return unique, len(items) - len(unique)

    try:
        matrix = TfidfVectorizer(stop_words="english").fit_transform(
            [it["content"] for it in unique]
        )
        sims = cosine_similarity(matrix)
    except ValueError:  # empty vocabulary
        return unique, len(items) - len(unique)

    kept: list[int] = []
    for i in range(len(unique)):
        if all(sims[i][j] < threshold for j in kept):
            kept.append(i)
    result = [unique[i] for i in kept]
    return result, len(items) - len(result)
