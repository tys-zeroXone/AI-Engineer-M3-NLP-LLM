from __future__ import annotations
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

def _env(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None or v == "":
        raise ValueError(f"Missing required env var: {name}")
    return v

@dataclass(frozen=True)
class Settings:
    OPENAI_API_KEY: str = _env("OPENAI_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    QDRANT_URL: str = _env("QDRANT_URL")
    QDRANT_API_KEY: str = _env("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "resumes_collection")

    TOP_K_DEFAULT: int = int(os.getenv("TOP_K_DEFAULT", "5"))
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

SETTINGS = Settings()
