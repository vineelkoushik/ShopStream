from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    KAFKA_BOOTSTRAP: str = "localhost:29092"
    REDIS_URL: str = "redis://localhost:6379/0"
    class Config:
        env_file = ".env"  
        extra = "ignore"

settings = Settings()
