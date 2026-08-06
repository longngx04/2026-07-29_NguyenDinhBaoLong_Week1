"""
Configuration management for Week 3 Security Analysis Agent.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def _load_dotenv(dotenv_path: Optional[Path] = None) -> None:
    if dotenv_path is None:
        dotenv_path = Path(__file__).resolve().parent.parent / ".env"
    if not dotenv_path.exists():
        return
    try:
        for line in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = val
    except OSError:
        pass  # .env missing or unreadable — optional file


@dataclass
class AppConfig:
    """Application configuration for Week 3 pipeline."""
    
    # Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    knowledge_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "knowledge")
    schema_path: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "schemas" / "security-analysis-record.schema.json")
    default_input: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "results" / "normalized" / "findings.json")
    default_output: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "results" / "analysis" / "security-analysis.jsonl")
    default_summary: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "results" / "analysis" / "run-summary.json")
    
    # LLM Settings
    provider_type: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "openrouter"))
    model_name: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "deepseek/deepseek-v4-flash-0731"))
    api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"))
    timeout: float = field(default_factory=lambda: float(
        os.getenv("LLM_TIMEOUT_SECONDS", os.getenv("LLM_TIMEOUT", "60"))
    ))
    max_retries: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_RETRIES", "1")))
    
    # Analysis Limits & Parameters
    top_k_knowledge: int = 3
    source_radius: int = 4  # lines around finding line
    max_snippet_chars: int = 700
    near_dup_line_threshold: int = 5

    def ensure_openrouter_ready(self) -> None:
        """Ensure OpenRouter configuration is valid before attempting network requests."""
        if self.provider_type != "openrouter":
            return
        if not self.api_key.strip():
            raise ValueError("LLM_API_KEY is required when LLM_PROVIDER=openrouter")
        if not self.base_url.startswith("https://"):
            raise ValueError("LLM_BASE_URL must be an HTTPS URL")

    @classmethod
    def from_env(cls, dotenv_path: Optional[Path] = None) -> "AppConfig":
        """Factory method creating AppConfig instance from environment variables."""
        _load_dotenv(dotenv_path=dotenv_path)
        return cls()
