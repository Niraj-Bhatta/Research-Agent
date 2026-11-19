"""Writer Agent – produces an IEEE-style report from research notes.

The writer follows IEEE conference paper conventions:
  Title  →  Abstract  →  I. INTRODUCTION  →  II-N. Body sections  →  CONCLUSION  →  REFERENCES
All headings use Roman numerals and uppercase. The References section is
appended automatically by the export node so the writer must NOT include one.
"""

from ..llm import chat

SYSTEM = """\
You are a professional IEEE technical report writer.  Write a report in Markdown
using IEEE conference paper structure and conventions.

Required sections (use EXACTLY these headings):
  # <Title>
  ## Abstract
  ## I. INTRODUCTION
  ## II. <SECTION>          ← use Roman numerals for each body section
  ## III. <SECTION>         ← add as many body sections as needed
  ## IV. CONCLUSION

Rules:
- Use uppercase Roman numerals for section numbers (I, II, III …).
- Keep all heading text UPPERCASE except the title.
- Use ONLY the research notes provided.  Do not invent facts.
- Cite claims inline like [1] or [2][5].  Only use numbers from the source list.
- Do NOT write a References section; it is appended automatically.
- Be clear, objective, and professional.
- Write in third person; avoid first person."""


def writer_node(state: dict) -> dict:
    notes = "\n\n".join(
        f"### {t['question']}\n{state['notes'][t['id']]}" for t in state["plan"]
    )
    sources = "\n".join(
        f"[{s['id']}] {s['title']} - {s['url']}" for s in state["sources"]
    )
    prompt = f"Title: {state['title']}\n\nResearch notes:\n{notes}\n\nValid sources:\n{sources}"

    revisions = state.get("revisions", 0)
    review = state.get("review")
    if review and not review.get("approved"):
        issues = "\n".join(f"- {i}" for i in review["issues"])
        prompt += (
            f"\n\nYour previous draft:\n{state['draft']}\n\n"
            f"A reviewer found these problems.  Fix them all:\n{issues}"
        )
        revisions += 1

    draft = chat(SYSTEM, prompt, max_tokens=6000)
    return {"draft": draft, "revisions": revisions, "stage": "writing"}
