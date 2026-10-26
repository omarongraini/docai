from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str

    # provider selection
    llm_provider: str = "openai"
    embedder_provider: str = "openai"
    vector_store_provider: str = "pgvector"

    # openai
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    

    # openai
    openai_embed_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"


    # tuning
    embedding_dim: int = 1536
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5
    language: str = "en"

settings = Settings()