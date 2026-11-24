import os

from dotenv import load_dotenv

load_dotenv()


class UserConfig:
    """Конфігурація мікросервісу користувачів та БД user-db."""

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "USER_DATABASE_URL",
        "postgresql+psycopg://user_svc:user_pass@localhost:5433/user_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "super-secret-jwt-key-change-in-production",
    )
