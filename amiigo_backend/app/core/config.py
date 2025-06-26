import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Define the base directory of the project
# This helps in locating .env files correctly, especially when running from different directories.
# BASE_DIR = Path(__file__).resolve().parent.parent.parent # amiigo_backend/
# For .env at project root (amiigo_backend/.env)
ENV_FILE_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    """
    Application settings.
    Values are loaded from environment variables or an .env file.
    """
    # --- General Application Settings ---
    APP_NAME: str = "Amiigo API"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1" # Base path for API version 1

    # --- Database Settings ---
    # Example: postgresql+psycopg2://user:password@host:port/dbname
    # DATABASE_URL: Optional[str] = "postgresql+psycopg2://user:password@localhost:5432/amiigo_db"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "amiigo_user"
    POSTGRES_PASSWORD: str = "amiigo_password"
    POSTGRES_DB: str = "amiigo_db"

    # Assembled DATABASE_URL
    # Note: Pydantic v2 doesn't have @validator, use model_validator or computed_field
    # For simplicity here, we'll assemble it in session.py or when used.
    # A more robust way would be to use a @computed_field if available or a property.
    # For now, this structure is fine, and we can create the full URL string when needed.
    # Example of how it would be constructed:
    # f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    SQLALCHEMY_DATABASE_URI: Optional[str] = None # Will be constructed

    # --- Security Settings (JWT) ---
    SECRET_KEY: str = "a_very_secret_key_that_should_be_changed_and_kept_safe" # CHANGE THIS!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- CORS (Cross-Origin Resource Sharing) ---
    # List of allowed origins. Use ["*"] to allow all, but be specific in production.
    # BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:4200", "http://localhost:8080"] # Example for Angular dev
    BACKEND_CORS_ORIGINS: list[str] = ["*"] # Allow all for now, refine later


    # --- Project Paths ---
    # BASE_DIR: Path = BASE_DIR # Defined above

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH), # Path to your .env file
        env_file_encoding='utf-8',
        case_sensitive=True,        # Environment variable names are case-sensitive
        extra='ignore'              # Ignore extra fields from .env that are not in Settings
    )

# Instantiate settings
settings = Settings()

# You can print settings for verification during development
# if __name__ == "__main__":
#     print("Current Settings:")
#     print(f"  APP_NAME: {settings.APP_NAME}")
#     print(f"  DEBUG: {settings.DEBUG}")
#     print(f"  API_V1_STR: {settings.API_V1_STR}")
#     print(f"  POSTGRES_SERVER: {settings.POSTGRES_SERVER}")
#     print(f"  POSTGRES_USER: {settings.POSTGRES_USER}")
#     print(f"  POSTGRES_PASSWORD: {'*' * len(settings.POSTGRES_PASSWORD) if settings.POSTGRES_PASSWORD else None}")
#     print(f"  POSTGRES_DB: {settings.POSTGRES_DB}")
#     print(f"  SECRET_KEY: {'*' * len(settings.SECRET_KEY) if settings.SECRET_KEY else None}")
#     print(f"  ALGORITHM: {settings.ALGORITHM}")
#     print(f"  ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
#     print(f"  BACKEND_CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")
#     print(f"  SQLALCHEMY_DATABASE_URI (to be constructed): {settings.SQLALCHEMY_DATABASE_URI}")
#     print(f"  .env file path used: {ENV_FILE_PATH}")

# Create a dummy .env file for demonstration if it doesn't exist
# In a real scenario, this .env file should be created manually and gitignored.
# For the sandbox, we'll create a default one.
if not ENV_FILE_PATH.exists():
    example_env_content = """
# .env - Environment variables for Amiigo Backend
# Copy this to .env and fill in your actual values.
# This file should be in your .gitignore

# Application Settings
APP_NAME="Amiigo API (Dev)"
DEBUG=True

# PostgreSQL Database Connection
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=amiigo_user
POSTGRES_PASSWORD=supersecretpassword # Change this!
POSTGRES_DB=amiigo_dev_db

# JWT Secret Key - Generate a strong random key for production
# openssl rand -hex 32
SECRET_KEY="your-super-secret-and-long-jwt-secret-key-here" # CHANGE THIS!
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080 # 7 days

# CORS Origins (space-separated if multiple, or use JSON array format if pydantic supports it directly for lists)
# For pydantic-settings, list[str] usually expects a JSON-formatted string array or comma-separated.
# Let's assume comma-separated for simplicity for now or JSON string.
# BACKEND_CORS_ORIGINS='["http://localhost:4200", "http://localhost:3000"]'
BACKEND_CORS_ORIGINS='["*"]' # Allow all for initial dev, restrict later
"""
    with open(ENV_FILE_PATH, "w") as f:
        f.write(example_env_content)
    print(f"Created a sample .env file at: {ENV_FILE_PATH}")

# Re-initialize settings to load from the newly created .env if it wasn't there before
settings = Settings()

# Construct SQLALCHEMY_DATABASE_URI from other settings
if not settings.SQLALCHEMY_DATABASE_URI and settings.POSTGRES_USER:
    settings.SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
elif not settings.SQLALCHEMY_DATABASE_URI:
     # Fallback if POSTGRES_USER is not set (e.g. if DATABASE_URL was directly provided)
    settings.SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db" # Default fallback to SQLite for local dev if no PG
    print("Warning: POSTGRES_USER not found in settings. Falling back to SQLite for DATABASE_URL.")


# Example: How to use in other modules:
# from app.core.config import settings
# db_url = settings.SQLALCHEMY_DATABASE_URI
# print(db_url)
# ``` # Removed offending backticks
