"""
Application Configuration.

This module defines the global settings for the application using Pydantic's BaseSettings.
It reads configuration variables from environment variables (e.g., .env file) to ensure
secrets and sensitive data are kept separate from the codebase.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application settings.

    Attributes are loaded from environment variables.
    """

    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    api_v1_str: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
