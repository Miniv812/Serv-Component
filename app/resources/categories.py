from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.auth import get_current_user_id, get_current_user_roles, roles_required
from app.extensions import db
from app.models import CategoryModel
from app.schemas import CategoryCreateSchema, CategoryDTOSchema

categories_bp = Blueprint("categories", __name__)
category_create_schema = CategoryCreateSchema()
category_dto_schema = CategoryDTOSchema()
categories_dto_schema = CategoryDTOSchema(many=True)


@categories_bp.route("/category", methods=["GET"])
@jwt_required()
def get_categories() -> tuple[Response, int]:
    """Перегляд категорій: user бачить глобальні та власні; auditor/admin — усі."""
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
    return jsonify(categories_dto_schema.dump(categories)), 200


@categories_bp.route("/category", methods=["POST"])
@roles_required("user", "admin")
def create_personal_category() -> tuple[Response, int]:
    """Створення персональної категорії для поточного користувача."""
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

    category = CategoryModel(name=name, user_id=get_current_user_id())
    db.session.add(category)
    db.session.commit()
    return jsonify(category_dto_schema.dump(category)), 201


@categories_bp.route("/category/global", methods=["POST"])
@roles_required("admin")
def create_global_category() -> tuple[Response, int]:
    """Створення глобальної категорії, видимої всім користувачам (тільки admin)."""
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

    category = CategoryModel(name=name, user_id=None)
    db.session.add(category)
    db.session.commit()
    return jsonify(category_dto_schema.dump(category)), 201


@categories_bp.route("/category/<int:category_id>", methods=["DELETE"])
@roles_required("user", "admin")
def delete_category(category_id: int) -> tuple[Response | str, int]:
    """Видалення категорії: admin — будь-яку, user — тільки власну персональну."""
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

    roles = get_current_user_roles()
    current_user_id = get_current_user_id()

    if "admin" not in roles:
        if category.user_id is None:
            return (
                jsonify(
                    {
                        "error": "forbidden",
                        "message": "Only administrators can delete global categories",
                    }
                ),
                403,
            )
        if category.user_id != current_user_id:
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
