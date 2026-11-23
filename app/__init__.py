from flask import Flask

from app.resources.categories import categories_bp
from app.resources.records import records_bp
from app.resources.users import users_bp
from app.views import health_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(health_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(records_bp)
    return app
