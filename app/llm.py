"""LLM wrapper – talks to any OpenAI-compatible endpoint."""

import json
import re
import time

from openai import OpenAI, RateLimitError, APIStatusError

from .config import settings

_client: OpenAI | None = None
_client_config: tuple[str, str] | None = None


def _get_client() -> OpenAI:
    global _client, _client_config
    current_config = (settings.base_url, settings.api_key)
    if _client is None or _client_config != current_config:
        _client = OpenAI(
            api_key=settings.api_key or "none",
            base_url=settings.base_url,
            timeout=45.0,
            max_retries=0,
        )
        _client_config = current_config
    return _client


def chat(system: str, user: str, max_tokens: int = 4096) -> str:
    """Send a system + user prompt and return the assistant reply as text."""
    client = _get_client()
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=settings.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return resp.choices[0].message.content or ""

        except RateLimitError as exc:
            # 429 – fail fast, don't retry
            raise RuntimeError(
                f"LLM rate-limited (429). Check API key quota for "
                f"provider='{settings.provider}' model='{settings.model}'. "
                f"Detail: {exc}"
            ) from exc

        except APIStatusError as exc:
            status = exc.status_code
            # Log full error body so we can see the exact reason
            print(f"[llm] HTTP {status} from {settings.provider}/{settings.model}: {exc.message}")

            if status in (400, 401, 403):
                # 400 Bad Request, 401/403 Auth – never retryable
                raise RuntimeError(
                    f"LLM error {status} (not retryable). "
                    f"provider='{settings.provider}' model='{settings.model}'. "
                    f"Detail: {exc.message}"
                ) from exc

            # Transient 5xx – wait briefly then retry
            if attempt < 2:
                wait = 5 * (attempt + 1)
                print(f"[llm] retrying in {wait}s (attempt {attempt + 1}/3)")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"LLM server error {status} after 3 attempts: {exc.message}"
                ) from exc

        except Exception as exc:
            if attempt < 2:
                wait = 5 * (attempt + 1)
                print(f"[llm] unexpected error, retrying in {wait}s: {exc}")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError("LLM call failed after 3 attempts.")


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
