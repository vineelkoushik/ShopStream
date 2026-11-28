
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://app:shopstream_secret_123@localhost:5432/ai_db"
    JWT_SECRET: str = "super_secret_key_change_me_later"
    JWT_ALGORITHM: str = "HS256"
    KAFKA_BOOTSTRAP: str = "localhost:29092"
    GROQ_API_KEY: str = ""
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
