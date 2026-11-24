import os

import pytest
from app import create_app
from app.auth import hash_password
from app.extensions import db as _db
from app.models import UserModel
from flask_jwt_extended import create_access_token


@pytest.fixture()
def app():
    """Створює тестовий екземпляр застосунку з ізольованою БД."""
    test_db_uri = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": test_db_uri,
            "JWT_SECRET_KEY": "test-secret-key-for-pytest",
        }
    )

    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    """Повертає тестовий HTTP-клієнт Flask."""
    return app.test_client()


def _create_user_with_token(username: str, name: str, role: str) -> tuple[int, dict]:
    user = UserModel(
        username=username,
        name=name,
        password_hash=hash_password("SecretPass123"),
        role=role,
    )
    _db.session.add(user)
    _db.session.commit()
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"roles": [user.role], "username": user.username},
    )
    return user.id, {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_users(app):
    """Створює набір користувачів усіх ролей (user1, user2, auditor, admin)."""
    with app.app_context():
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
