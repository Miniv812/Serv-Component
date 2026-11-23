from flask import Blueprint, Response, jsonify, request

from app.storage import storage

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/category", methods=["GET"])
def get_categories() -> tuple[Response, int]:
    """Отримання списку всіх категорій."""
    return jsonify(storage.get_all_categories()), 200


@categories_bp.route("/category", methods=["POST"])
def create_category() -> tuple[Response, int]:
    """Створення нової категорії витрат."""
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

    category = storage.create_category(name=name.strip())
    return jsonify(category), 201


@categories_bp.route("/category/<int:category_id>", methods=["DELETE"])
def delete_category(category_id: int) -> tuple[Response | str, int]:
    """Видалення категорії за ідентифікатором."""
    deleted = storage.delete_category(category_id)
    if not deleted:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Category with id {category_id} not found",
                }
            ),
            404,
        )
    return "", 204
