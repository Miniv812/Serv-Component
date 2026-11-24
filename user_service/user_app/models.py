from user_app.extensions import db


class UserModel(db.Model):
    """ORM-модель користувача в ізольованій базі user-db."""

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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "role": self.role,
        }
