from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError

from app.extensions import db
from app.models import AccountModel, UserModel
from app.schemas import AccountCreateSchema, AccountDepositSchema, AccountDTOSchema

accounts_bp = Blueprint("accounts", __name__)
account_create_schema = AccountCreateSchema()
account_deposit_schema = AccountDepositSchema()
account_dto_schema = AccountDTOSchema()
accounts_dto_schema = AccountDTOSchema(many=True)


@accounts_bp.route("/account", methods=["POST"])
def create_account() -> tuple[Response, int]:
    """Створення нового рахунку користувача."""
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

    user = db.session.get(UserModel, data["user_id"])
    if user is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"User with id {data['user_id']} not found",
                }
            ),
            404,
        )

    account = AccountModel(
        user_id=data["user_id"],
        balance=data["balance"],
    )
    db.session.add(account)
    db.session.commit()
    return jsonify(account_dto_schema.dump(account)), 201


@accounts_bp.route("/account/<int:account_id>", methods=["GET"])
def get_account(account_id: int) -> tuple[Response, int]:
    """Отримання інформації та балансу рахунку."""
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
    return jsonify(account_dto_schema.dump(account)), 200


@accounts_bp.route("/user/<int:user_id>/accounts", methods=["GET"])
def get_user_accounts(user_id: int) -> tuple[Response, int]:
    """Отримання списку рахунків конкретного користувача."""
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
def deposit_account(account_id: int) -> tuple[Response, int]:
    """Поповнення балансу рахунку користувача."""
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
