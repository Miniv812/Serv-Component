from flask import Flask

from user_app import models  # noqa: F401
from user_app.auth import register_jwt_handlers
from user_app.config import UserConfig
from user_app.extensions import db, jwt, migrate
from user_app.resources.auth import auth_bp
from user_app.resources.users import users_bp
from user_app.views import health_bp


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(UserConfig)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    register_jwt_handlers(jwt)

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    return app
