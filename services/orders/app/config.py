from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://app:shopstream_secret_123@localhost:5432/order_db"
    JWT_SECRET: str = "super_secret_key_change_me_later"
    JWT_ALGORITHM: str = "HS256"
    PRODUCT_SERVICE_URL: str = "http://localhost:8002"
    PAYMENT_SERVICE_URL: str = "http://localhost:8004"
    KAFKA_BOOTSTRAP: str = "localhost:29092"
    REDIS_URL: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()