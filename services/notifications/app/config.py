
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://app:shopstream_secret_123@localhost:5432/notification_db"
    JWT_SECRET: str = "super_secret_key_change_me_later"
    JWT_ALGORITHM: str = "HS256"
    KAFKA_BOOTSTRAP: str = "localhost:29092"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


