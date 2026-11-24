from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import jsonify
from flask_jwt_extended import JWTManager, get_jwt, get_jwt_identity, jwt_required
from passlib.hash import argon2


def hash_password(password: str) -> str:
    """Генерує криптографічно стійкий Argon2id-хеш пароля."""
    return argon2.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Перевіряє пароль проти збереженого Argon2-хешу."""
    return argon2.verify(password, hashed)


def get_current_user_id() -> int:
    """Повертає цілочисельний ID поточного користувача з JWT."""
    return int(get_jwt_identity())


def get_current_user_roles() -> list[str]:
    """Повертає список ролей поточного користувача з JWT Claims."""
    return get_jwt().get("roles", [])


def roles_required(*required_roles: str) -> Callable:
    """Декоратор перевірки ролей доступу користувача (RBAC)."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        @jwt_required()
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            user_roles = get_current_user_roles()

            if not any(role in user_roles for role in required_roles):
                return (
                    jsonify(
                        {
                            "error": "forbidden",
                            "message": "Access denied: insufficient privileges",
                        }
                    ),
                    403,
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def register_jwt_handlers(jwt_manager: JWTManager) -> None:
    """Налаштування стандартних HTTP 401 відповідей для помилок JWT."""

    @jwt_manager.unauthorized_loader
    def handle_missing_token(reason: str) -> tuple[Any, int]:
        return jsonify({"error": "unauthorized", "message": reason}), 401

    @jwt_manager.invalid_token_loader
    def handle_invalid_token(reason: str) -> tuple[Any, int]:
        return jsonify({"error": "invalid_token", "message": reason}), 401

    @jwt_manager.expired_token_loader
    def handle_expired_token(
        jwt_header: dict,
        jwt_payload: dict,
    ) -> tuple[Any, int]:
        return (
            jsonify(
                {
                    "error": "token_expired",
                    "message": "Access token has expired",
                }
            ),
            401,
        )
