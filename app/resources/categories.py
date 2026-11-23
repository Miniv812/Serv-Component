from flask import Blueprint, Response, jsonify, request
from marshmallow import ValidationError

from app.extensions import db
from app.models import CategoryModel
from app.schemas import CategoryCreateSchema, CategoryDTOSchema

categories_bp = Blueprint("categories", __name__)
category_create_schema = CategoryCreateSchema()
category_dto_schema = CategoryDTOSchema()
categories_dto_schema = CategoryDTOSchema(many=True)


@categories_bp.route("/category", methods=["GET"])
def get_categories() -> tuple[Response, int]:
    """Отримання списку всіх категорій із БД."""
    categories = CategoryModel.query.order_by(CategoryModel.id).all()
    return jsonify(categories_dto_schema.dump(categories)), 200


@categories_bp.route("/category", methods=["POST"])
def create_category() -> tuple[Response, int]:
    """Створення нової категорії з валідацією через Marshmallow."""
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
        data = category_create_schema.load(payload)
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

    category = CategoryModel(name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify(category_dto_schema.dump(category)), 201


@categories_bp.route("/category/<int:category_id>", methods=["DELETE"])
def delete_category(category_id: int) -> tuple[Response | str, int]:
    """Видалення категорії за ідентифікатором."""
    category = db.session.get(CategoryModel, category_id)
    if category is None:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": f"Category with id {category_id} not found",
                }
            ),
            404,
        )

    db.session.delete(category)
    db.session.commit()
    return "", 204
