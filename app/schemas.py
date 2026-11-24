from decimal import Decimal

from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validate,
    validates_schema,
)


class RegisterSchema(Schema):
    """Схема валідації реєстрації нового користувача."""

    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=80),
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128),
    )


class LoginSchema(Schema):
    """Схема валідації входу користувача в систему."""

    username = fields.Str(required=True)
    password = fields.Str(required=True)


class UserRoleUpdateSchema(Schema):
    """Схема валідації зміни ролі користувача адміністратором."""

    role = fields.Str(
        required=True,
        validate=validate.OneOf(["user", "auditor", "admin"]),
    )


class UserDTOSchema(Schema):
    """DTO-схема серіалізації користувача."""

    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    role = fields.Str(dump_only=True)


class CategoryCreateSchema(Schema):
    """Схема валідації вхідних даних для створення категорії."""

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
    )


class CategoryDTOSchema(Schema):
    """DTO-схема серіалізації категорії."""

    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True, allow_none=True)
    is_global = fields.Method("get_is_global", dump_only=True)

    def get_is_global(self, obj: object) -> bool:
        return getattr(obj, "user_id", None) is None


class AccountCreateSchema(Schema):
    """Схема валідації для створення рахунку користувача."""

    user_id = fields.Int(
        required=False,
        strict=True,
        validate=validate.Range(min=1),
    )
    balance = fields.Decimal(
        as_string=False,
        places=2,
        load_default=Decimal("0.00"),
        validate=validate.Range(min=Decimal("0.00")),
    )


class AccountDepositSchema(Schema):
    """Схема валідації для поповнення рахунку."""

    amount = fields.Decimal(
        required=True,
        as_string=False,
        places=2,
        validate=validate.Range(min=Decimal("0.01")),
    )


class AccountDTOSchema(Schema):
    """DTO-схема серіалізації рахунку користувача."""

    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    balance = fields.Float(dump_only=True)


class RecordCreateSchema(Schema):
    """Схема валідації вхідних даних для створення витрати."""

    user_id = fields.Int(
        required=False,
        strict=True,
        validate=validate.Range(min=1),
    )
    category_id = fields.Int(
        required=True,
        strict=True,
        validate=validate.Range(min=1),
    )
    amount = fields.Decimal(
        required=True,
        as_string=False,
        places=2,
        validate=validate.Range(min=Decimal("0.01")),
    )


class RecordFilterSchema(Schema):
    """Схема валідації query-параметрів фільтрації витрат."""

    user_id = fields.Int(
        required=False,
        validate=validate.Range(min=1),
    )
    category_id = fields.Int(
        required=False,
        validate=validate.Range(min=1),
    )

    @validates_schema
    def validate_at_least_one_filter(self, data: dict, **kwargs: object) -> None:
        if data.get("user_id") is None and data.get("category_id") is None:
            raise ValidationError(
                "At least one query parameter ('user_id' or 'category_id') "
                "is required for filtration"
            )


class RecordDTOSchema(Schema):
    """DTO-схема серіалізації запису витрати."""

    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    category_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    amount = fields.Float(dump_only=True)
