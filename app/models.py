from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db


class UserModel(db.Model):
    """ORM-модель користувача з обліковими даними та роллю"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(20),
        default="user",
        server_default="user",
        nullable=False,
    )

    categories = db.relationship(
        "CategoryModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    accounts = db.relationship(
        "AccountModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    records = db.relationship(
        "RecordModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "role": self.role,
        }


class CategoryModel(db.Model):
    """ORM-модель категорії витрат (глобальної або персональної)."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    user = db.relationship("UserModel", back_populates="categories")
    records = db.relationship(
        "RecordModel",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "is_global": self.user_id is None,
        }


class AccountModel(db.Model):
    """ORM-модель рахунку користувача"""

    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    balance = db.Column(
        db.Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    user = db.relationship("UserModel", back_populates="accounts")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "balance": float(self.balance),
        }


class RecordModel(db.Model):
    """ORM-модель запису витрати."""

    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    amount = db.Column(db.Numeric(12, 2), nullable=False)

    user = db.relationship("UserModel", back_populates="records")
    category = db.relationship("CategoryModel", back_populates="records")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "created_at": self.created_at.isoformat(),
            "amount": float(self.amount),
        }
