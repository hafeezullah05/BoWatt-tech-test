"""Application configuration.

Reads settings from environment variables (and a local .env file during
development) into a single typed object so the rest of the app never touches
os.environ directly.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    """Typed application settings loaded from environment variables.

    Attributes:
        anthropic_api_key: API key for the Claude models used by the agent.
        tavily_api_key: API key for the Tavily web-search tool.
        chroma_persist_dir: Filesystem path where the Chroma vector store
            persists embedded source chunks between server restarts.
        embedding_model_name: Name of the sentence-transformers model used
            to embed uploaded source text and research queries.
        claude_model_name: Claude model identifier used by the research agent.
        cors_origin: Origin allowed to call this API (the frontend's URL).
    """

    anthropic_api_key: str
    tavily_api_key: str
    chroma_persist_dir: str = "./chroma_data"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    claude_model_name: str = "claude-sonnet-4-5-20250929"
    cors_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Cached via lru_cache so the .env file and environment are only read
    once per process, and every module gets the same Settings object.
    """
    return Settings()