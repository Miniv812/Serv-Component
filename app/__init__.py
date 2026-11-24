from flask import Flask

from app import models  # noqa: F401
from app.auth import register_jwt_handlers
from app.config import Config
from app.extensions import db, jwt, migrate
from app.resources.accounts import accounts_bp
from app.resources.auth import auth_bp
from app.resources.categories import categories_bp
from app.resources.records import records_bp
from app.resources.users import users_bp
from app.views import health_bp


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    register_jwt_handlers(jwt)

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(records_bp)
    return app
