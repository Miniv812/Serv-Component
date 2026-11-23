from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError

from app.extensions import db
from app.models import AccountModel, CategoryModel, RecordModel, UserModel
from app.schemas import RecordCreateSchema, RecordDTOSchema, RecordFilterSchema

records_bp = Blueprint("records", __name__)
record_create_schema = RecordCreateSchema()
record_filter_schema = RecordFilterSchema()
record_dto_schema = RecordDTOSchema()
records_dto_schema = RecordDTOSchema(many=True)


@records_bp.route("/record", methods=["POST"])
def create_record() -> tuple[Response, int]:
    """Створення витрати з автоматичним списанням з рахунку (Варіант 3)."""
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

    account = AccountModel.query.filter_by(user_id=data["user_id"]).first()
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
        user_id=data["user_id"],
        category_id=data["category_id"],
        amount=data["amount"],
    )
    db.session.add(record)
    db.session.commit()

    response_data = record_dto_schema.dump(record)
    response_data["remaining_balance"] = float(account.balance)
    return jsonify(response_data), 201


@records_bp.route("/record/<int:record_id>", methods=["GET"])
def get_record(record_id: int) -> tuple[Response, int]:
    """Отримання запису витрати за ідентифікатором."""
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
    return jsonify(record_dto_schema.dump(record)), 200


@records_bp.route("/record/<int:record_id>", methods=["DELETE"])
def delete_record(record_id: int) -> tuple[Response | str, int]:
    """Видалення запису витрати за ідентифікатором."""
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

    db.session.delete(record)
    db.session.commit()
    return "", 204


@records_bp.route("/record", methods=["GET"])
def get_records() -> tuple[Response, int]:
    """Фільтрація записів витрат за user_id та/або category_id."""
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

    query = RecordModel.query
    if "user_id" in filters:
        query = query.filter_by(user_id=filters["user_id"])
    if "category_id" in filters:
        query = query.filter_by(category_id=filters["category_id"])

    records = query.order_by(RecordModel.id).all()
    return jsonify(records_dto_schema.dump(records)), 200
