from flask import Flask

from app import models  # noqa: F401
from app.config import Config
from app.extensions import db, migrate
from app.resources.categories import categories_bp
from app.resources.records import records_bp
from app.resources.users import users_bp
from app.views import health_bp


def create_app() -> Flask:

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(health_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(records_bp)
    return app
