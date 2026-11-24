import logging
from typing import Any, cast

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

from user_app.auth import hash_password, verify_password
from user_app.extensions import db
from user_app.models import UserModel
from user_app.schemas import LoginSchema, RegisterSchema, UserDTOSchema

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)
register_schema = RegisterSchema()
login_schema = LoginSchema()
user_dto_schema = UserDTOSchema()


@auth_bp.route("/register", methods=["POST"])
def register() -> tuple[Response, int]:
    """Публічна реєстрація користувача в User Service."""
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
        data = cast(dict[str, Any], register_schema.load(payload))
    except ValidationError as err:
        return jsonify({"error": "validation_error", "messages": err.messages}), 400

    username = data["username"].strip()
    name = data["name"].strip()
    if not username or not name:
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": "Fields 'username' and 'name' cannot be blank",
                }
            ),
            400,
        )

    existing = UserModel.query.filter_by(username=username).first()
    if existing is not None:
        return (
            jsonify(
                {
                    "error": "user_exists",
                    "message": f"Username '{username}' is already taken",
                }
            ),
            409,
        )

    user = UserModel(
        username=username,
        name=name,
        password_hash=hash_password(data["password"]),
        role="user",
    )
    db.session.add(user)
    db.session.commit()

    logger.info("Registered new user username=%s id=%s", user.username, user.id)
    return jsonify(user_dto_schema.dump(user)), 201


@auth_bp.route("/login", methods=["POST"])
def login() -> tuple[Response, int]:
    """Аутентифікація користувача та видача Access JWT."""
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
        data = cast(dict[str, Any], login_schema.load(payload))
    except ValidationError as err:
        return jsonify({"error": "validation_error", "messages": err.messages}), 400

    user = UserModel.query.filter_by(username=data["username"].strip()).first()
    if user is None or not verify_password(data["password"], user.password_hash):
        logger.warning(
            "Failed login attempt for username=%s",
            data["username"].strip(),
        )
        return (
            jsonify(
                {
                    "error": "invalid_credentials",
                    "message": "Invalid username or password",
                }
            ),
            401,
        )

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "roles": [user.role],
            "username": user.username,
        },
    )

    logger.info("User logged in username=%s id=%s", user.username, user.id)
    return (
        jsonify(
            {
                "access_token": access_token,
                "user": user_dto_schema.dump(user),
            }
        ),
        200,
    )
