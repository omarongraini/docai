from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str

    # provider selection
    llm_provider: str = "openai"
    embed_provider: str = "openai"
    vector_store_provider: str = "pgvector"

    llm_api_key: str
    llm_base_url: str = "https://api.openai.com/v1"
    llm_chat_model: str = "gpt-4o-mini"

    relevance_cutoff: float = 0.75

    # embed
    embed_model: str = "text-embedding-3-small"
    embed_api_key: str
    embed_base_url: str

    embed_dim: int = 1536

    # tuning
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5
    language: str = "en"


settings = Settings()
