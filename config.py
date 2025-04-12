from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file for local development.
load_dotenv()


class Settings(BaseSettings):
    """
    Application configuration settings.

    """

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # JWT Authentication configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

    class Config:
        # Specify the .env file for loading environment variables.
        env_file = ".env"
        env_file_encoding = "utf-8"

