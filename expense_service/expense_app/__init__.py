from flask import Flask

from expense_app import models  # noqa: F401
from expense_app.auth import register_jwt_handlers
from expense_app.config import ExpenseConfig
from expense_app.extensions import db, jwt, migrate
from expense_app.resources.accounts import accounts_bp
from expense_app.resources.categories import categories_bp
from expense_app.resources.records import records_bp
from expense_app.resources.rpc import rpc_bp
from expense_app.views import health_bp


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(ExpenseConfig)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    register_jwt_handlers(jwt)

    app.register_blueprint(health_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(rpc_bp)
    return app
