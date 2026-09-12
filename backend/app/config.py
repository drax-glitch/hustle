import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

_IS_PRODUCTION = os.getenv("FLASK_ENV", "development").lower() == "production"


def _require_env(name, dev_default):
    value = os.getenv(name)
    if value:
        return value
    if _IS_PRODUCTION:
        print(f"FATAL: {name} must be set in production", file=sys.stderr)
        sys.exit(1)
    return dev_default


class Config:
    SECRET_KEY = _require_env("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = _require_env("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "life_rpg")

    if os.getenv("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    elif DB_TYPE == "mysql" and DB_PASSWORD:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'life_rpg.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    DEBUG = not _IS_PRODUCTION and os.getenv("FLASK_DEBUG", "1") == "1"

    # Security settings
    if _IS_PRODUCTION:
        SESSION_COOKIE_SECURE = True
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = 'Lax'

    # AI / Game Master Configuration
    AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # openai, anthropic, mock
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")
    AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "10"))  # seconds
