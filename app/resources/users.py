from flask import Blueprint, Response, jsonify, request

from app.storage import storage

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["GET"])
def get_users() -> tuple[Response, int]:
    """Отримання списку всіх користувачів."""
    return jsonify(storage.get_all_users()), 200


@users_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id: int) -> tuple[Response, int]:
    """Отримання користувача за ідентифікатором."""
    user = storage.get_user(user_id)
    if user is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"User with id {user_id} not found",
                }
            ),
            404,
        )
    return jsonify(user), 200


@users_bp.route("/user", methods=["POST"])
def create_user() -> tuple[Response, int]:
    """Створення нового користувача."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return (
            jsonify(
                {
                    "error": "invalid_request",
                    "message": "Request body must be a valid JSON object",
                }
            ),
            400,
        )

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": (
                        "Field 'name' is required and must be a non-empty string"
                    ),
                }
            ),
            400,
        )

    user = storage.create_user(name=name.strip())
    return jsonify(user), 201


@users_bp.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int) -> tuple[Response | str, int]:
    """Видалення користувача за ідентифікатором."""
    deleted = storage.delete_user(user_id)
    if not deleted:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"User with id {user_id} not found",
                }
            ),
            404,
        )
    return "", 204
