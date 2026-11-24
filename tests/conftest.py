import os
import socket

import pytest
from flask_jwt_extended import create_access_token

from expense_app import create_app as create_expense_app
from expense_app.extensions import db as _expense_db
from user_app import create_app as create_user_app
from user_app.auth import hash_password
from user_app.extensions import db as _user_db
from user_app.grpc_server import create_grpc_server
from user_app.models import UserModel

TEST_JWT_SECRET = "test-microservices-jwt-secret-key"


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture()
def user_app():
    """Тестовий екземпляр User Service з ізольованою БД."""
    db_uri = os.getenv("TEST_USER_DATABASE_URL", "sqlite:///:memory:")
    application = create_user_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": db_uri,
            "JWT_SECRET_KEY": TEST_JWT_SECRET,
        }
    )

    with application.app_context():
        _user_db.create_all()
        yield application
        _user_db.session.remove()
        _user_db.drop_all()


@pytest.fixture()
def user_client(user_app):
    """HTTP-клієнт для User Service."""
    return user_app.test_client()


@pytest.fixture()
def grpc_server_addr(user_app):
    """Запускає реальний gRPC AuthService з RBACServerInterceptor на вільному порту."""
    port = _get_free_port()
    server = create_grpc_server(user_app, port=port)
    server.start()
    yield f"127.0.0.1:{port}"
    server.stop(grace=0)


@pytest.fixture()
def expense_app(grpc_server_addr):
    """Тестовий екземпляр Expense Service, підключений до gRPC User Service."""
    db_uri = os.getenv("TEST_EXPENSE_DATABASE_URL", "sqlite:///:memory:")
    application = create_expense_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": db_uri,
            "JWT_SECRET_KEY": TEST_JWT_SECRET,
            "USER_SERVICE_GRPC_ADDR": grpc_server_addr,
        }
    )

    with application.app_context():
        _expense_db.create_all()
        yield application
        _expense_db.session.remove()
        _expense_db.drop_all()


@pytest.fixture()
def expense_client(expense_app):
    """HTTP-клієнт для Expense Service."""
    return expense_app.test_client()


def _create_user_with_token(username: str, name: str, role: str) -> tuple[int, dict]:
    user = UserModel(
        username=username,
        name=name,
        password_hash=hash_password("SecretPass123"),
        role=role,
    )
    _user_db.session.add(user)
    _user_db.session.commit()
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"roles": [user.role], "username": user.username},
    )
    return user.id, {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_users(user_app):
    """Створює набір користувачів усіх ролей (user1, user2, auditor, admin) у user-db"""
    with user_app.app_context():
        u1_id, u1_header = _create_user_with_token("vlad", "Vladyslav", "user")
        u2_id, u2_header = _create_user_with_token("bob", "Bob", "user")
        aud_id, aud_header = _create_user_with_token("auditor1", "Auditor", "auditor")
        adm_id, adm_header = _create_user_with_token("admin1", "Admin", "admin")
        return {
            "user1": {"id": u1_id, "headers": u1_header},
            "user2": {"id": u2_id, "headers": u2_header},
            "auditor": {"id": aud_id, "headers": aud_header},
            "admin": {"id": adm_id, "headers": adm_header},
        }
