from collections.abc import Callable
from typing import Any

import grpc
from flask import Flask
from flask_jwt_extended import decode_token


def _abort_handler(code: grpc.StatusCode, details: str) -> grpc.RpcMethodHandler:
    """Повертає gRPC-обробник, який перериває запит із заданим статус-кодом."""

    def abort(request: Any, context: grpc.ServicerContext) -> None:
        context.abort(code, details)

    return grpc.unary_unary_rpc_method_handler(abort)


class RBACServerInterceptor(grpc.ServerInterceptor):
    """Серверний gRPC Interceptor для перевірки JWT та ролей доступу (RBAC)."""

    def __init__(self, app: Flask, method_roles_map: dict[str, list[str]]) -> None:
        self.app = app
        self.method_roles_map = method_roles_map

    def _validate_and_check_roles(
        self,
        token: str,
        required_roles: list[str],
    ) -> bool:
        raw_token = token.removeprefix("Bearer ").strip()
        if not raw_token:
            return False

        try:
            with self.app.app_context():
                decoded = decode_token(raw_token)
        except Exception:
            return False

        user_roles = decoded.get("roles", [])
        return any(role in user_roles for role in required_roles)

    def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        method = handler_call_details.method
        required_roles = self.method_roles_map.get(method, [])

        if required_roles:
            metadata = dict(handler_call_details.invocation_metadata)
            token = metadata.get("authorization")

            if not token or not self._validate_and_check_roles(
                token,
                required_roles,
            ):
                return _abort_handler(
                    grpc.StatusCode.PERMISSION_DENIED,
                    "Access denied by gRPC RBAC Interceptor",
                )

        return continuation(handler_call_details)
