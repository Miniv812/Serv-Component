import logging
from typing import Any, cast

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from expense_app.auth import get_current_user_id, get_current_user_roles
from expense_app.extensions import db
from expense_app.grpc_client import verify_user_via_grpc
from expense_app.models import AccountModel, CategoryModel, RecordModel
from expense_app.schemas import (
    AccountCreateSchema,
    AccountDepositSchema,
    AccountDTOSchema,
    CategoryDTOSchema,
    RecordCreateSchema,
    RecordDTOSchema,
    RecordFilterSchema,
)
from observability.metrics import record_expense_created

logger = logging.getLogger(__name__)

rpc_bp = Blueprint("rpc", __name__)

record_create_schema = RecordCreateSchema()
record_filter_schema = RecordFilterSchema()
record_dto_schema = RecordDTOSchema()
records_dto_schema = RecordDTOSchema(many=True)

account_create_schema = AccountCreateSchema()
account_deposit_schema = AccountDepositSchema()
account_dto_schema = AccountDTOSchema()
categories_dto_schema = CategoryDTOSchema(many=True)


class JsonRpcError(Exception):
    """Виняток для формування стандартної помилки JSON-RPC 2.0."""

    def __init__(self, code: int, message: str, data: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


def _error_response(
    req_id: Any,
    code: int,
    message: str,
    data: Any = None,
) -> dict[str, Any]:
    error_obj: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error_obj["data"] = data
    return {
        "jsonrpc": "2.0",
        "error": error_obj,
        "id": req_id,
    }


def _success_response(req_id: Any, result: Any) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "result": result,
        "id": req_id,
    }


def _rpc_create_record(params: dict[str, Any], auth_header: str) -> dict[str, Any]:
    roles = get_current_user_roles()
    if not any(r in roles for r in ("user", "admin")):
        raise JsonRpcError(-32600, "Access denied: insufficient privileges")

    try:
        data = cast(dict[str, Any], record_create_schema.load(params))
    except ValidationError as err:
        raise JsonRpcError(-32602, "Invalid params", err.messages) from err

    current_user_id = get_current_user_id()
    if "admin" in roles and "user_id" in data:
        target_user_id = data["user_id"]
    else:
        if "user_id" in data and data["user_id"] != current_user_id:
            raise JsonRpcError(-32600, "Cannot create expense record for another user")
        target_user_id = current_user_id

    is_valid, _, grpc_error = verify_user_via_grpc(target_user_id, auth_header)
    if not is_valid:
        raise JsonRpcError(-32600, grpc_error or "User verification failed via gRPC")

    category = db.session.get(CategoryModel, data["category_id"])
    if category is None:
        raise JsonRpcError(-32602, f"Category with id {data['category_id']} not found")

    if (
        "admin" not in roles
        and category.user_id is not None
        and category.user_id != target_user_id
    ):
        raise JsonRpcError(-32602, f"Category with id {data['category_id']} not found")

    account = AccountModel.query.filter_by(user_id=target_user_id).first()
    if account is None or account.balance < data["amount"]:
        raise JsonRpcError(
            -32602,
            "Insufficient account balance or account not found",
        )

    account.balance -= data["amount"]
    record = RecordModel(
        user_id=target_user_id,
        category_id=data["category_id"],
        amount=data["amount"],
    )
    db.session.add(record)
    db.session.commit()

    record_expense_created(float(data["amount"]), channel="json_rpc")
    logger.info(
        "Created JSON-RPC expense record id=%s user_id=%s amount=%s",
        record.id,
        target_user_id,
        float(data["amount"]),
    )

    return {
        "record_id": record.id,
        "status": "created",
        "user_id": record.user_id,
        "category_id": record.category_id,
        "amount": float(record.amount),
        "remaining_balance": float(account.balance),
    }


def _rpc_get_records(params: dict[str, Any], auth_header: str) -> list[dict[str, Any]]:
    try:
        filters = cast(dict[str, Any], record_filter_schema.load(params))
    except ValidationError as err:
        raise JsonRpcError(-32602, "Invalid params", err.messages) from err

    roles = get_current_user_roles()
    current_user_id = get_current_user_id()

    query = RecordModel.query
    if "admin" not in roles and "auditor" not in roles:
        if "user_id" in filters and filters["user_id"] != current_user_id:
            raise JsonRpcError(-32600, "Access denied: can only filter own records")
        query = query.filter_by(user_id=current_user_id)
    elif "user_id" in filters:
        query = query.filter_by(user_id=filters["user_id"])

    if "category_id" in filters:
        query = query.filter_by(category_id=filters["category_id"])

    records = query.order_by(RecordModel.id).all()
    return cast(list[dict[str, Any]], records_dto_schema.dump(records))


def _rpc_create_account(params: dict[str, Any], auth_header: str) -> dict[str, Any]:
    roles = get_current_user_roles()
    if not any(r in roles for r in ("user", "admin")):
        raise JsonRpcError(-32600, "Access denied: insufficient privileges")

    try:
        data = cast(dict[str, Any], account_create_schema.load(params))
    except ValidationError as err:
        raise JsonRpcError(-32602, "Invalid params", err.messages) from err

    current_user_id = get_current_user_id()
    if "admin" in roles and "user_id" in data:
        target_user_id = data["user_id"]
    else:
        if "user_id" in data and data["user_id"] != current_user_id:
            raise JsonRpcError(-32600, "Cannot create account for another user")
        target_user_id = current_user_id

    is_valid, _, grpc_error = verify_user_via_grpc(target_user_id, auth_header)
    if not is_valid:
        raise JsonRpcError(-32600, grpc_error or "User verification failed via gRPC")

    account = AccountModel(user_id=target_user_id, balance=data["balance"])
    db.session.add(account)
    db.session.commit()
    return cast(dict[str, Any], account_dto_schema.dump(account))


def _rpc_deposit_account(params: dict[str, Any], auth_header: str) -> dict[str, Any]:
    roles = get_current_user_roles()
    if not any(r in roles for r in ("user", "admin")):
        raise JsonRpcError(-32600, "Access denied: insufficient privileges")

    account_id = params.get("account_id")
    if not isinstance(account_id, int) or isinstance(account_id, bool):
        raise JsonRpcError(-32602, "Invalid params: 'account_id' must be an integer")

    account = db.session.get(AccountModel, account_id)
    if account is None:
        raise JsonRpcError(-32602, f"Account with id {account_id} not found")

    if "admin" not in roles and account.user_id != get_current_user_id():
        raise JsonRpcError(-32600, "Access denied to this account")

    try:
        data = cast(
            dict[str, Any],
            account_deposit_schema.load({"amount": params.get("amount")}),
        )
    except ValidationError as err:
        raise JsonRpcError(-32602, "Invalid params", err.messages) from err

    account.balance += data["amount"]
    db.session.commit()
    return cast(dict[str, Any], account_dto_schema.dump(account))


def _rpc_get_categories(params: dict[str, Any],
                        auth_header: str) -> list[dict[str, Any]]:
    roles = get_current_user_roles()
    current_user_id = get_current_user_id()

    if "admin" in roles or "auditor" in roles:
        categories = CategoryModel.query.order_by(CategoryModel.id).all()
    else:
        categories = (
            CategoryModel.query.filter(
                (CategoryModel.user_id.is_(None))
                | (CategoryModel.user_id == current_user_id)
            )
            .order_by(CategoryModel.id)
            .all()
        )
    return cast(list[dict[str, Any]], categories_dto_schema.dump(categories))


RPC_METHODS = {
    "create_record": _rpc_create_record,
    "get_records": _rpc_get_records,
    "create_account": _rpc_create_account,
    "deposit_account": _rpc_deposit_account,
    "get_categories": _rpc_get_categories,
}


def _process_single_rpc(item: Any, auth_header: str) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return _error_response(None, -32600, "Invalid Request")

    has_id = "id" in item
    req_id = item.get("id")

    if item.get("jsonrpc") != "2.0":
        return _error_response(req_id, -32600, "Invalid Request: jsonrpc must be '2.0'")

    method = item.get("method")
    if not isinstance(method, str) or not method:
        return _error_response(req_id, -32600, "Invalid Request: method must be string")

    params = item.get("params", {})
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return _error_response(req_id, -32602, "Invalid params: expected JSON object")

    handler = RPC_METHODS.get(method)
    if handler is None:
        if not has_id:
            return None
        return _error_response(req_id, -32601, f"Method '{method}' not found")

    try:
        result = handler(params, auth_header)
    except JsonRpcError as err:
        db.session.rollback()
        if not has_id:
            return None
        return _error_response(req_id, err.code, err.message, err.data)
    except Exception as err:
        db.session.rollback()
        if not has_id:
            return None
        return _error_response(req_id, -32603, "Internal error", str(err))

    if not has_id:
        return None
    return _success_response(req_id, result)


@rpc_bp.route("/rpc", methods=["POST"])
@jwt_required()
def handle_rpc() -> tuple[Response | str, int]:
    """Публічний ендпоінт JSON-RPC 2.0 із підтримкою Single та Batch запитів."""
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify(_error_response(None, -32700, "Parse error: invalid JSON")), 400

    auth_header = request.headers.get("Authorization", "")

    if isinstance(payload, list):
        if len(payload) == 0:
            return (
                jsonify(_error_response(None, -32600, "Invalid Request: empty batch")),
                400,
            )
        responses = []
        for item in payload:
            res = _process_single_rpc(item, auth_header)
            if res is not None:
                responses.append(res)
        if not responses:
            return "", 204
        return jsonify(responses), 200

    if isinstance(payload, dict):
        res = _process_single_rpc(payload, auth_header)
        if res is None:
            return "", 204
        return jsonify(res), 200

    return jsonify(_error_response(None, -32600, "Invalid Request")), 400
