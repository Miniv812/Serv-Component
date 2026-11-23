from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError

from app.extensions import db
from app.models import UserModel
from app.schemas import UserCreateSchema, UserDTOSchema

users_bp = Blueprint("users", __name__)
user_create_schema = UserCreateSchema()
user_dto_schema = UserDTOSchema()
users_dto_schema = UserDTOSchema(many=True)


@users_bp.route("/users", methods=["GET"])
def get_users() -> tuple[Response, int]:
    """Отримання списку всіх користувачів із БД."""
    users = UserModel.query.order_by(UserModel.id).all()
    return jsonify(users_dto_schema.dump(users)), 200


@users_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id: int) -> tuple[Response, int]:
    """Отримання користувача за ідентифікатором."""
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


@users_bp.route("/user", methods=["POST"])
def create_user() -> tuple[Response, int]:
    """Створення нового користувача з валідацією через Marshmallow."""
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
        data = user_create_schema.load(payload)
    except ValidationError as err:
        return jsonify({"error": "validation_error", "messages": err.messages}), 400

    name = data["name"].strip()
    if not name:
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "messages": {"name": ["Name cannot be blank."]},
                }
            ),
            400,
        )

    user = UserModel(name=name)
    db.session.add(user)
    db.session.commit()
    return jsonify(user_dto_schema.dump(user)), 201


@users_bp.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int) -> tuple[Response | str, int]:
    """Видалення користувача за ідентифікатором."""
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
