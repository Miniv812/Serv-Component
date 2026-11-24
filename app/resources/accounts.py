from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.auth import get_current_user_id, get_current_user_roles, roles_required
from app.extensions import db
from app.models import AccountModel, UserModel
from app.schemas import AccountCreateSchema, AccountDepositSchema, AccountDTOSchema

accounts_bp = Blueprint("accounts", __name__)
account_create_schema = AccountCreateSchema()
account_deposit_schema = AccountDepositSchema()
account_dto_schema = AccountDTOSchema()
accounts_dto_schema = AccountDTOSchema(many=True)


@accounts_bp.route("/account", methods=["POST"])
@roles_required("user", "admin")
def create_account() -> tuple[Response, int]:
    """Створення рахунку: user — лише для себе, admin — для будь-кого."""
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
        data = account_create_schema.load(payload)
    except ValidationError as err:
        return jsonify({"error": "validation_error", "messages": err.messages}), 400

    roles = get_current_user_roles()
    current_user_id = get_current_user_id()

    if "admin" in roles and "user_id" in data:
        target_user_id = data["user_id"]
    else:
        if "user_id" in data and data["user_id"] != current_user_id:
            return (
                jsonify(
                    {
                        "error": "forbidden",
                        "message": "Cannot create account for another user",
                    }
                ),
                403,
            )
        target_user_id = current_user_id

    user = db.session.get(UserModel, target_user_id)
    if user is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"User with id {target_user_id} not found",
                }
            ),
            404,
        )

    account = AccountModel(
        user_id=target_user_id,
        balance=data["balance"],
    )
    db.session.add(account)
    db.session.commit()
    return jsonify(account_dto_schema.dump(account)), 201


@accounts_bp.route("/account/<int:account_id>", methods=["GET"])
@jwt_required()
def get_account(account_id: int) -> tuple[Response, int]:
    """Отримання балансу рахунку: user — лише свій, auditor/admin — будь-який."""
    account = db.session.get(AccountModel, account_id)
    if account is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Account with id {account_id} not found",
                }
            ),
            404,
        )

    roles = get_current_user_roles()
    if "admin" not in roles and "auditor" not in roles:
        if account.user_id != get_current_user_id():
            return (
                jsonify(
                    {
                        "error": "not_found",
                        "message": f"Account with id {account_id} not found",
                    }
                ),
                404,
            )

    return jsonify(account_dto_schema.dump(account)), 200


@accounts_bp.route("/user/<int:user_id>/accounts", methods=["GET"])
@jwt_required()
def get_user_accounts(user_id: int) -> tuple[Response, int]:
    """Отримання рахунків користувача з урахуванням прав доступу."""
    roles = get_current_user_roles()
    if "admin" not in roles and "auditor" not in roles:
        if user_id != get_current_user_id():
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
    return jsonify(accounts_dto_schema.dump(user.accounts)), 200


@accounts_bp.route("/account/<int:account_id>/deposit", methods=["POST"])
@roles_required("user", "admin")
def deposit_account(account_id: int) -> tuple[Response, int]:
    """Поповнення рахунку: user — лише свій, admin — будь-який."""
    account = db.session.get(AccountModel, account_id)
    if account is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Account with id {account_id} not found",
                }
            ),
            404,
        )

    roles = get_current_user_roles()
    if "admin" not in roles and account.user_id != get_current_user_id():
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Account with id {account_id} not found",
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
        data = account_deposit_schema.load(payload)
    except ValidationError as err:
        return jsonify({"error": "validation_error", "messages": err.messages}), 400

    account.balance += data["amount"]
    db.session.commit()
    return jsonify(account_dto_schema.dump(account)), 200
