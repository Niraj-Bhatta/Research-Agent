"""Reviewer Agent – evaluates the draft for completeness, citations, and style."""

import re

from ..llm import chat_json

SYSTEM = """\
You are a strict IEEE paper reviewer.  Evaluate the draft on:
1. Structure: has Abstract, Introduction, body sections with Roman numerals, Conclusion
2. Readability: clear, well structured, no repetition
3. Citation quality: claims are cited, citation numbers exist in the source list
Return JSON: {"approved": true/false, "score": 1-10, "issues": ["specific fix", ...]}
Approve (true) only if score >= 8.  Keep issues specific and actionable."""


def reviewer_node(state: dict) -> dict:
    valid_ids = {s["id"] for s in state["sources"]}
    cited_ids = {int(n) for n in re.findall(r"\[(\d+)\]", state["draft"])}
    invalid = sorted(cited_ids - valid_ids)

    prompt = (
        f"Valid source numbers: {sorted(valid_ids)}\n"
        f"Citation numbers used in draft: {sorted(cited_ids)}\n\n"
        f"Draft:\n{state['draft']}"
    )
    review = chat_json(SYSTEM, prompt)

    if invalid:
        review["approved"] = False
        review.setdefault("issues", []).append(
            f"Draft cites non-existent sources {invalid}.  Remove or fix them."
        )
    return {"review": review, "stage": "reviewing"}
