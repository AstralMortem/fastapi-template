from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from pathlib import Path


class Settings(BaseSettings):
    DEBUG: bool = False

    GLOBAL_API_PREFIX: str = "/api"
    LOGIN_URL_ENDPOINT: str = "/api/v1/auth/login"

    # DB
    DATABASE_URL: PostgresDsn | str = "sqlite+aiosqlite:///./test.db"
    DEFAULT_USER_IS_ACTIVE: bool = True
    DEFAULT_USER_IS_VERIFIED: bool = False
    DEFAULT_USER_ROLE_ID: int = 1

    # AUTH
    LOGIN_FIELDS: list[str] = ["email"]
    ALLOW_INACIVE_USER_LOGIN: bool = False
    ALLOW_UNVERIFIED_USER_LOGIN: bool = False

    # JWT
    SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MAX_AGE: int = 60 * 60 * 12
    ACCESS_TOKEN_AUDIENCE: list[str] = ["auth"]

    # FS
    PROJECT_DIR: Path = Path(__file__).parent.absolute()
    ALEMBIC_INI_PATH: Path = (
        Path(__file__).parent.parent.parent.joinpath("alembic.ini").absolute()
    )

    # LOGGING
    LOGGER_NAME: str = "app"
    LOGGER_LOG_FILE_PATH: Path = Path(".").joinpath("app.log")
    LOGGER_OUT_IN_CONSOLE: bool = True
    LOGGER_OUT_IN_FILE: bool = True

    # CELERY
    CELERY_BACKEND_URL: str = ''
    CELERY_BROKER_URL: str = ''


settings = Settings()
