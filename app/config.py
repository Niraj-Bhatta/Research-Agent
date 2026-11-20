"""Application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

# Load .env BEFORE reading any os.getenv calls
load_dotenv(override=True)

# Provider → (base_url, api‑key env var, default model)
PROVIDERS = {
    "gemini": (
        "https://generativelanguage.googleapis.com/v1beta/openai/",
        "GEMINI_API_KEY",
        "gemini-flash-lite-latest",
    ),
    "groq": (
        "https://api.groq.com/openai/v1",
        "GROQ_API_KEY",
        "llama-3.3-70b-versatile",
    ),
    "openrouter": (
        "https://openrouter.ai/api/v1",
        "OPENROUTER_API_KEY",
        "meta-llama/llama-3.3-70b-instruct:free",
    ),
    "ollama": (
        "http://localhost:11434/v1",
        "",
        "llama3.1",
    ),
    "anthropic": (
        "https://api.anthropic.com/v1/",
        "ANTHROPIC_API_KEY",
        "claude-sonnet-5-5",
    ),
}


class Settings:
    """Centralised settings – all values resolved at instantiation time
    so that load_dotenv() has already populated os.environ."""

    def __init__(self) -> None:
        self.provider: str = os.getenv("LLM_PROVIDER", "openrouter").lower()

        if self.provider not in PROVIDERS:
            raise ValueError(
                f"Unknown LLM_PROVIDER '{self.provider}'. "
                f"Choose from: {list(PROVIDERS)}"
            )

        _base, _key_env, _default_model = PROVIDERS[self.provider]

        self.base_url: str = os.getenv("LLM_BASE_URL", _base)
        self.api_key: str = os.getenv(_key_env, "") if _key_env else "ollama"
        self.model: str = os.getenv("LLM_MODEL", _default_model)

        self.tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

        self.max_revisions: int = int(os.getenv("MAX_REVISIONS", "2"))
        self.dedup_threshold: float = float(os.getenv("DEDUP_THRESHOLD", "0.85"))
        self.results_per_query: int = int(os.getenv("RESULTS_PER_QUERY", "5"))
        self.output_dir: str = os.getenv("OUTPUT_DIR", "outputs")


# Centralised settings loaded from environment
settings = Settings()
