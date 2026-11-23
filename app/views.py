from datetime import datetime, timezone

from flask import Blueprint, Response, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/healthz")


@health_bp.route("/live", methods=["GET"])
def liveness_check() -> tuple[Response, int]:
    """Перевірка життєздатності процесу застосунку (Liveness)."""
    return (
        jsonify(
            {
                "status": "alive",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ),
        200,
    )


@health_bp.route("/ready", methods=["GET"])
def readiness_check() -> tuple[Response, int]:
    """Перевірка готовності застосунку та підключення до БД (Readiness)."""
    try:
        db.session.execute(text("SELECT 1"))
        return (
            jsonify(
                {
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
                    "status": "not_ready",
                    "database": "unavailable",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            503,
        )
