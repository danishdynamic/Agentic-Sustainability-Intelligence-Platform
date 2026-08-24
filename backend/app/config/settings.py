from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-flash-lite"
    gemini_embedding_model: str = "models/text-embedding-004"
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@postgres:5432/sustainability"
    )
    redis_url: str = "redis://redis:6379/0"
    knowledge_path: str = "knowledge"
    embedding_dimensions: int = 768
    retrieval_top_k: int = 20
    rerank_top_k: int = 8
    max_rag_retries: int = 2
    chunk_size: int = 900
    chunk_overlap: int = 120
    cache_ttl_seconds: int = 3600
    semantic_cache_enabled: bool = True
    semantic_cache_threshold: float = 0.92
    max_input_length: int = 2000
    max_output_length: int = 8000
    otel_enabled: bool = True
    otel_service_name: str = "sustainability-agent"
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"
    checkpoint_enabled: bool = True
    gemini_max_rpm: int = 15
    gemini_max_tpm: int = 250000
    gemini_max_rpd: int = 500

    model_config = SettingsConfigDict(env_file=(".env", "backend/.env"), extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
