from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.auth import get_current_user_id, get_current_user_roles, roles_required
from app.extensions import db
from app.models import UserModel
from app.schemas import UserDTOSchema, UserRoleUpdateSchema

users_bp = Blueprint("users", __name__)
user_dto_schema = UserDTOSchema()
users_dto_schema = UserDTOSchema(many=True)
role_update_schema = UserRoleUpdateSchema()


@users_bp.route("/users", methods=["GET"])
@roles_required("auditor", "admin")
def get_users() -> tuple[Response, int]:
    """Отримання списку всіх користувачів (тільки auditor та admin)."""
    users = UserModel.query.order_by(UserModel.id).all()
    return jsonify(users_dto_schema.dump(users)), 200


@users_bp.route("/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id: int) -> tuple[Response, int]:
    """Отримання профілю: user бачить лише свій, auditor/admin — будь-який."""
    roles = get_current_user_roles()
    current_user_id = get_current_user_id()

    if "admin" not in roles and "auditor" not in roles:
        if current_user_id != user_id:
            return (
                jsonify(
                    {
                        "error": "not_found",
                        "message": f"User with id {user_id} not found",
                    }
                ),
                404,
            )

    user = db.session.get(UserModel, user_id)
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
    return jsonify(user_dto_schema.dump(user)), 200


@users_bp.route("/user/<int:user_id>", methods=["DELETE"])
@roles_required("admin")
def delete_user(user_id: int) -> tuple[Response | str, int]:
    """Видалення користувача за ідентифікатором (тільки admin)."""
    user = db.session.get(UserModel, user_id)
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

    db.session.delete(user)
    db.session.commit()
    return "", 204


@users_bp.route("/user/<int:user_id>/role", methods=["PATCH"])
@roles_required("admin")
def update_user_role(user_id: int) -> tuple[Response, int]:
    """Зміна ролі користувача (тільки admin)."""
    user = db.session.get(UserModel, user_id)
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

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return (
            jsonify(
                {
                    "error": "invalid_request",
                    "message": "Request body must be a valid JSON object",
                }
            ),
            400,
        )

    try:
        data = role_update_schema.load(payload)
    except ValidationError as err:
        return jsonify({"error": "validation_error", "messages": err.messages}), 400

    user.role = data["role"]
    db.session.commit()
    return jsonify(user_dto_schema.dump(user)), 200
