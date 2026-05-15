# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SECRET_KEY: str = "super-secret-evaluation-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 1 day

    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SENDER_EMAIL: str = "absolutecinema360@gmail.com"
    SENDER_PASSWORD: str = ""

    STRIPE_API_KEY: str = ""
    # Browser-facing Streamlit URL (Stripe redirects, local dev uses localhost:8501)
    FRONTEND_BASE_URL: str = "http://localhost:8501"

settings = Settings()
