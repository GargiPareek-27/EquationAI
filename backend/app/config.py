# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    frontend_url: str = "http://localhost:3000"
    gemini_model_name: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"

settings = Settings()  # raises at import time if GEMINI_API_KEY is missing — fail fast, not on first request