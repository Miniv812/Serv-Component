import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфігурація застосунку, БД та JWT-аутентифікації."""

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://expense_user:expense_pass@localhost:5432/expense_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "super-secret-jwt-key-change-in-production",
    )
