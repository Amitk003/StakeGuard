"""Settings loader for StakeGuard.

Reads values from the .env file and environment variables. The .env file is
never committed to the repository.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def api_key() -> str:
    """Return the LLM API key, or an empty string if not set."""
    return os.getenv("OPENAI_API_KEY", "")


def base_url() -> str | None:
    """Return the LLM base URL override, or None if not set."""
    return os.getenv("OPENAI_BASE_URL") or None


def model() -> str:
    """Return the configured LLM model name, or a default."""
    return os.getenv("LLM_MODEL", "gpt-4o-mini")
