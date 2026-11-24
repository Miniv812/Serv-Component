import logging
import os
import threading
from concurrent import futures

import grpc
from flask import Flask
from flask_jwt_extended import decode_token
from grpc_reflection.v1alpha import reflection

from proto import auth_pb2, auth_pb2_grpc
from user_app.extensions import db
from user_app.interceptors import RBACServerInterceptor
from user_app.models import UserModel

logger = logging.getLogger(__name__)


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
    """Реалізація gRPC-сервісу аутентифікації та перевірки користувачів."""

    def __init__(self, app: Flask) -> None:
        self.app = app

    def ValidateToken(  # noqa: N802
        self,
        request: auth_pb2.ValidateTokenRequest,
        context: grpc.ServicerContext,
    ) -> auth_pb2.ValidateTokenResponse:
        raw_token = request.token.removeprefix("Bearer ").strip()
        if not raw_token:
            return auth_pb2.ValidateTokenResponse(is_valid=False)

        with self.app.app_context():
            try:
                decoded = decode_token(raw_token)
                user_id = int(decoded["sub"])
            except Exception:
                return auth_pb2.ValidateTokenResponse(is_valid=False)

            user = db.session.get(UserModel, user_id)
            if user is None:
                return auth_pb2.ValidateTokenResponse(is_valid=False)

            return auth_pb2.ValidateTokenResponse(
                is_valid=True,
                user_id=str(user.id),
                roles=[user.role],
            )

    def ValidateUser(  # noqa: N802
        self,
        request: auth_pb2.UserRequest,
        context: grpc.ServicerContext,
    ) -> auth_pb2.UserResponse:
        with self.app.app_context():
            user = db.session.get(UserModel, request.user_id)
            if user is None:
                return auth_pb2.UserResponse(exists=False, role="")

            return auth_pb2.UserResponse(exists=True, role=user.role)


def create_grpc_server(app: Flask, port: int = 50051) -> grpc.Server:
    """Створює та конфігурує екземпляр gRPC-сервера з RBAC Interceptor."""
    method_roles_map = {
        "/auth.AuthService/ValidateUser": ["user", "auditor", "admin"],
    }
    interceptor = RBACServerInterceptor(app=app, method_roles_map=method_roles_map)

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[interceptor],
    )
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServicer(app), server)

    service_names = (
        auth_pb2.DESCRIPTOR.services_by_name["AuthService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)

    server.add_insecure_port(f"0.0.0.0:{port}")
    return server


def start_grpc_server_in_background(app: Flask, port: int | None = None) -> grpc.Server:
    """Запускає gRPC-сервер у фоновому потоці паралельно з Flask REST API."""
    grpc_port = port or int(os.getenv("USER_GRPC_PORT", "50051"))
    server = create_grpc_server(app, port=grpc_port)
    server.start()
    logger.info("gRPC AuthService started on port %s", grpc_port)

    thread = threading.Thread(target=server.wait_for_termination, daemon=True)
    thread.start()
    return server
