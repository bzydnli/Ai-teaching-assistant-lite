from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    chat_model: str = "gpt-5.6-luna"
    embedding_model: str = "text-embedding-3-small"
    database_url: str = "postgresql://postgres:postgres@localhost:5433/ai_teacher"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
