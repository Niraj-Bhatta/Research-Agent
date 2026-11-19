"""LLM wrapper – talks to the Gemini OpenAI-compatible endpoint.

One thin layer so every agent goes through the same retry / JSON-parse logic.
"""

import json
import re
import time

from openai import OpenAI, RateLimitError

from .config import settings

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.api_key or "none",
            base_url=settings.base_url,
            timeout=60.0,
        )
    return _client


def chat(system: str, user: str, max_tokens: int = 4096) -> str:
    """Send a system + user prompt and return the assistant reply as text."""
    for attempt in range(6):
        try:
            resp = _get_client().chat.completions.create(
                model=settings.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return resp.choices[0].message.content or ""
        except RateLimitError:
            wait = 15 * (attempt + 1)
            print(f"[rate-limited] waiting {wait}s  (attempt {attempt + 1}/6)")
            time.sleep(wait)
    raise RuntimeError("Rate limit kept failing – wait a minute or switch provider/model.")


def chat_json(system: str, user: str, max_tokens: int = 2048, retries: int = 2) -> dict:
    """Ask for JSON output and parse it, retrying on malformed replies."""
    sys_prompt = system + "\n\nRespond with valid JSON only. No markdown fences, no commentary."
    last_err: Exception | None = None
    for _ in range(retries + 1):
        text = chat(sys_prompt, user, max_tokens).strip()
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            last_err = exc
    raise ValueError(f"LLM returned invalid JSON after {retries + 1} tries: {last_err}")
