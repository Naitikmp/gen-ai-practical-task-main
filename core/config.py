import os
# from pydantic import BaseSettings
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    ENVIRONMENT: str

    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()

# Load settings
settings = get_settings() 
