from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from expense_app.auth import (
    get_current_user_id,
    get_current_user_roles,
    roles_required,
)
from expense_app.extensions import db
from expense_app.models import AccountModel, CategoryModel, RecordModel
from expense_app.schemas import RecordCreateSchema, RecordDTOSchema, RecordFilterSchema

records_bp = Blueprint("records", __name__)
record_create_schema = RecordCreateSchema()
record_filter_schema = RecordFilterSchema()
record_dto_schema = RecordDTOSchema()
records_dto_schema = RecordDTOSchema(many=True)


@records_bp.route("/record", methods=["POST"])
@roles_required("user", "admin")
def create_record() -> tuple[Response, int]:
    """Створення витрати з RBAC та списанням з рахунку (Варіант 3)."""
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
        data = record_create_schema.load(payload)
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
                        "message": "Cannot create expense record for another user",
                    }
                ),
                403,
            )
        target_user_id = current_user_id

    category = db.session.get(CategoryModel, data["category_id"])
    if category is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Category with id {data['category_id']} not found",
                }
            ),
            404,
        )

    if (
        "admin" not in roles
        and category.user_id is not None
        and category.user_id != target_user_id
    ):
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Category with id {data['category_id']} not found",
                }
            ),
            404,
        )

    account = AccountModel.query.filter_by(user_id=target_user_id).first()
    if account is None or account.balance < data["amount"]:
        return (
            jsonify(
                {
                    "error": "insufficient_funds",
                    "message": "Insufficient account balance or account not found",
                }
            ),
            400,
        )

    account.balance -= data["amount"]
    record = RecordModel(
        user_id=target_user_id,
        category_id=data["category_id"],
        amount=data["amount"],
    )
    db.session.add(record)
    db.session.commit()

    response_data = record_dto_schema.dump(record)
    response_data["remaining_balance"] = float(account.balance)
    return jsonify(response_data), 201


@records_bp.route("/record/<int:record_id>", methods=["GET"])
@jwt_required()
def get_record(record_id: int) -> tuple[Response, int]:
    """Отримання запису витрати: user — лише свій, auditor/admin — будь-який."""
    record = db.session.get(RecordModel, record_id)
    if record is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Record with id {record_id} not found",
                }
            ),
            404,
        )

    roles = get_current_user_roles()
    if "admin" not in roles and "auditor" not in roles:
        if record.user_id != get_current_user_id():
            return (
                jsonify(
                    {
                        "error": "not_found",
                        "message": f"Record with id {record_id} not found",
                    }
                ),
                404,
            )

    return jsonify(record_dto_schema.dump(record)), 200


@records_bp.route("/record/<int:record_id>", methods=["DELETE"])
@roles_required("user", "admin")
def delete_record(record_id: int) -> tuple[Response | str, int]:
    """Видалення витрати: user — лише власну, admin — будь-яку."""
    record = db.session.get(RecordModel, record_id)
    if record is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Record with id {record_id} not found",
                }
            ),
            404,
        )

    roles = get_current_user_roles()
    if "admin" not in roles and record.user_id != get_current_user_id():
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Record with id {record_id} not found",
                }
            ),
            404,
        )

    db.session.delete(record)
    db.session.commit()
    return "", 204


@records_bp.route("/record", methods=["GET"])
@jwt_required()
def get_records() -> tuple[Response, int]:
    """Фільтрація витрат: user — лише за своїм user_id; auditor/admin — за всіма."""
    if not request.args:
        return (
            jsonify(
                {
                    "error": "invalid_request",
                    "message": (
                        "At least one query parameter ('user_id' or "
                        "'category_id') is required for filtration"
                    ),
                }
            ),
            400,
        )

    try:
        filters = record_filter_schema.load(request.args.to_dict())
    except ValidationError as err:
        return jsonify({"error": "validation_error", "messages": err.messages}), 400

    roles = get_current_user_roles()
    current_user_id = get_current_user_id()

    query = RecordModel.query
    if "admin" not in roles and "auditor" not in roles:
        if "user_id" in filters and filters["user_id"] != current_user_id:
            return (
                jsonify(
                    {
                        "error": "forbidden",
                        "message": "Access denied: can only filter own records",
                    }
                ),
                403,
            )
        query = query.filter_by(user_id=current_user_id)
    elif "user_id" in filters:
        query = query.filter_by(user_id=filters["user_id"])

    if "category_id" in filters:
        query = query.filter_by(category_id=filters["category_id"])

    records = query.order_by(RecordModel.id).all()
    return jsonify(records_dto_schema.dump(records)), 200
