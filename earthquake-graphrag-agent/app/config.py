from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class Settings:
    cases_file: Path = Path(os.getenv("CASES_FILE", "data/cases.json"))
    runtime_memory_file: Path = Path(os.getenv("MEMORY_FILE", "runtime_memory.json"))
    feedback_file: Path = Path(os.getenv("FEEDBACK_FILE", "feedback_cases.json"))

    # Anthropic / Claude API
    use_anthropic: bool = os.getenv("USE_ANTHROPIC", "0") == "1"
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    anthropic_base_url: str | None = os.getenv("ANTHROPIC_BASE_URL") or None

    # Ollama
    use_ollama: bool = os.getenv("USE_OLLAMA", "0") == "1"
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")


settings = Settings()
