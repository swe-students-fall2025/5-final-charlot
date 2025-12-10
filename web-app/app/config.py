"""Configuration settings for the app"""

import pathlib

from pydantic_settings import BaseSettings

DIR = pathlib.Path(__file__).parent.parent


class Settings(BaseSettings):
    """fastAPI app settings class"""

    # Defaults so the app still runs even if .env is missing
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "legal_ai"
    jwt_secret_key: str = "supersecret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class ConfigDict:
        """Config file"""

        env_file = DIR / ".env"


_settings = None  # pylint: disable=invalid-name


def get_settings() -> Settings:
    """Set settings"""

    global _settings  # pylint: disable=global-statement
    if _settings is None:
        _settings = Settings()
    return _settings
