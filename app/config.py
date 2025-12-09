from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Defaults so the app still runs even if .env is missing
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "legal_ai"
    jwt_secret_key: str = "supersecret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class ConfigDict:
        env_file = ".env"


_settings = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
