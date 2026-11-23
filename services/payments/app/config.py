from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://app:shopstream_secret_123@localhost:5432/payment_db"
    JWT_SECRET: str = "super_secret_key_change_me_later"
    JWT_ALGORITHM: str = "HS256"
    PAYMENT_MAX_AMOUNT: float = 10000.0
    PAYMENT_FAIL_RATE: float = 0.0
    KAFKA_BOOTSTRAP: str = "localhost:29092"
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()