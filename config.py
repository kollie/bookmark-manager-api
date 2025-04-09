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

    This class loads configuration values from the environment,
    falling back to provided default values if they are not set.
    It includes settings for the database connection, JWT authentication,
    and allowed CORS origins.
    """

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # JWT Authentication configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS configuration: expected as a comma-separated list in the environment variable.
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

    class Config:
        # Specify the .env file for loading environment variables.
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Retrieve the application settings using caching.

    The LRU cache ensures that settings are loaded only once,
    which improves performance by avoiding repeated reads from disk.

    Returns:
        Settings: An instance containing the application's configuration.
    """
    return Settings()
