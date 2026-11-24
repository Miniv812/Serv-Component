import os

from dotenv import load_dotenv

load_dotenv()


class ExpenseConfig:
    """Конфігурація мікросервісу витрат та БД expense-db."""

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "EXPENSE_DATABASE_URL",
        "postgresql+psycopg://expense_svc:expense_pass@localhost:5432/expense_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "super-secret-jwt-key-change-in-production",
    )
    USER_SERVICE_GRPC_ADDR = os.getenv(
        "USER_SERVICE_GRPC_ADDR",
        "localhost:50051",
    )
