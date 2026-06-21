from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# This finds the .env file one folder up from backend/
ENV_FILE = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Nexora"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "nexora_super_secret_key_change_this_in_production_2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

   # AI
    # AI
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = str(ENV_FILE)

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()