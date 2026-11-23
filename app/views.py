from datetime import datetime, timezone

from flask import Blueprint, Response, jsonify

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
    """Перевірка готовності застосунку до обробки трафіку (Readiness)."""
    return (
        jsonify(
            {
                "status": "ready",
                "database": "not_connected_yet",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ),
        200,
    )