from decimal import Decimal, InvalidOperation

from flask import Blueprint, Response, jsonify, request

from app.storage import storage

records_bp = Blueprint("records", __name__)


@records_bp.route("/record", methods=["POST"])
def create_record() -> tuple[Response, int]:
    """Створення нового запису витрати."""
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

    user_id = data.get("user_id")
    category_id = data.get("category_id")
    raw_amount = data.get("amount")

    if isinstance(user_id, bool) or not isinstance(user_id, int):
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": "Field 'user_id' is required and must be an integer",
                }
            ),
            400,
        )

    if isinstance(category_id, bool) or not isinstance(category_id, int):
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": (
                        "Field 'category_id' is required and must be an integer"
                    ),
                }
            ),
            400,
        )

    if isinstance(raw_amount, bool) or not isinstance(raw_amount, (int, float, str)):
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": "Field 'amount' is required and must be a number",
                }
            ),
            400,
        )

    try:
        amount = Decimal(str(raw_amount))
    except InvalidOperation:
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": "Field 'amount' must be a valid decimal number",
                }
            ),
            400,
        )

    if not amount.is_finite() or amount <= 0:
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": "Field 'amount' must be greater than 0",
                }
            ),
            400,
        )

    if storage.get_user(user_id) is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"User with id {user_id} not found",
                }
            ),
            404,
        )

    if storage.get_category(category_id) is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Category with id {category_id} not found",
                }
            ),
            404,
        )

    record = storage.create_record(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
    )
    return jsonify(record), 201


@records_bp.route("/record/<int:record_id>", methods=["GET"])
def get_record(record_id: int) -> tuple[Response, int]:
    """Отримання запису витрати за ідентифікатором."""
    record = storage.get_record(record_id)
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
    return jsonify(record), 200


@records_bp.route("/record/<int:record_id>", methods=["DELETE"])
def delete_record(record_id: int) -> tuple[Response | str, int]:
    """Видалення запису витрати за ідентифікатором."""
    deleted = storage.delete_record(record_id)
    if not deleted:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Record with id {record_id} not found",
                }
            ),
            404,
        )
    return "", 204


@records_bp.route("/record", methods=["GET"])
def get_records() -> tuple[Response, int]:
    """Фільтрація записів витрат за user_id та/або category_id."""
    raw_user_id = request.args.get("user_id")
    raw_category_id = request.args.get("category_id")

    if raw_user_id is None and raw_category_id is None:
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

    user_id: int | None = None
    category_id: int | None = None

    if raw_user_id is not None:
        try:
            user_id = int(raw_user_id)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": "validation_error",
                        "message": "Query parameter 'user_id' must be an integer",
                    }
                ),
                400,
            )

    if raw_category_id is not None:
        try:
            category_id = int(raw_category_id)
        except ValueError:
            return (
                jsonify(
                    {
                        "error": "validation_error",
                        "message": (
                            "Query parameter 'category_id' must be an integer"
                        ),
                    }
                ),
                400,
            )

    records = storage.filter_records(user_id=user_id, category_id=category_id)
    return jsonify(records), 200
