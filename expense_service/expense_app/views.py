from datetime import datetime, timezone

from flask import Blueprint, Response, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from expense_app.extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/healthz")


@health_bp.route("/live", methods=["GET"])
def liveness_check() -> tuple[Response, int]:
    """Перевірка життєздатності Expense Service."""
    return (
        jsonify(
            {
                "service": "expense-service",
                "status": "alive",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ),
        200,
    )


@health_bp.route("/ready", methods=["GET"])
def readiness_check() -> tuple[Response, int]:
    """Перевірка готовності Expense Service та підключення до expense-db."""
    try:
        db.session.execute(text("SELECT 1"))
        return (
            jsonify(
                {
                    "service": "expense-service",
                    "status": "ready",
                    "database": "connected",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            200,
        )
    except SQLAlchemyError:
        return (
            jsonify(
                {
                    "service": "expense-service",
                    "status": "not_ready",
                    "database": "unavailable",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            503,
        )
