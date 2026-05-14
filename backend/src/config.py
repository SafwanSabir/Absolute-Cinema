# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "super-secret-evaluation-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 1 day

    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SENDER_EMAIL: str = "absolutecinema360@gmail.com"
    SENDER_PASSWORD: str = ""

    STRIPE_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
