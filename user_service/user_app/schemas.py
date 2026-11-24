from marshmallow import Schema, fields, validate


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
