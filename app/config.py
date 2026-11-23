import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфігурація застосунку та підключення до PostgreSQL."""

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://expense_user:expense_pass@localhost:5432/expense_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
