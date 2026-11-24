import logging
import time
from collections.abc import Callable
from typing import Any

import grpc
from flask import current_app

from observability.metrics import record_grpc_validation
from proto import auth_pb2, auth_pb2_grpc

logger = logging.getLogger(__name__)


class _ClientCallDetails(grpc.ClientCallDetails):
    """Опис параметрів клієнтського gRPC-виклику з оновленими метаданими."""

    def __init__(
        self,
        method: str,
        timeout: float | None,
        metadata: tuple[tuple[str, str | bytes], ...] | None,
        credentials: grpc.CallCredentials | None,
        wait_for_ready: bool | None,
        compression: grpc.Compression | None,
    ) -> None:
        self.method = method
        self.timeout = timeout
        self.metadata = metadata
        self.credentials = credentials
        self.wait_for_ready = wait_for_ready
        self.compression = compression


class AuthClientInterceptor(grpc.UnaryUnaryClientInterceptor):
    """Клієнтський gRPC Interceptor для передачі Bearer-токена у gRPC Metadata."""

    def __init__(self, auth_header: str) -> None:
        self.auth_header = auth_header

    def intercept_unary_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.ClientCallDetails,
        request: Any,
    ) -> Any:
        metadata: list[tuple[str, str | bytes]] = list(
            client_call_details.metadata or ()
        )
        if self.auth_header:
            metadata.append(("authorization", self.auth_header))

        new_details = _ClientCallDetails(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            metadata=tuple(metadata),
            credentials=client_call_details.credentials,
            wait_for_ready=client_call_details.wait_for_ready,
            compression=client_call_details.compression,
        )
        return continuation(new_details, request)


def verify_user_via_grpc(
    user_id: int,
    auth_header: str,
) -> tuple[bool, str | None, str | None]:
    """Синхронний gRPC-виклик до User Service для перевірки користувача та ролі.

    Повертає кортеж: (is_valid, role, error_message).
    """
    grpc_addr = current_app.config.get(
        "USER_SERVICE_GRPC_ADDR",
        "localhost:50051",
    )
    interceptor = AuthClientInterceptor(auth_header=auth_header)
    start_time = time.perf_counter()

    try:
        with grpc.insecure_channel(grpc_addr) as base_channel:
            channel = grpc.intercept_channel(base_channel, interceptor)
            stub = auth_pb2_grpc.AuthServiceStub(channel)
            logger.info(
                "Sending gRPC ValidateUser request for user_id=%s to %s",
                user_id,
                grpc_addr,
            )
            response = stub.ValidateUser(
                auth_pb2.UserRequest(user_id=user_id),
                timeout=5.0,
            )
    except grpc.RpcError as err:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        if err.code() in (
            grpc.StatusCode.PERMISSION_DENIED,
            grpc.StatusCode.UNAUTHENTICATED,
        ):
            record_grpc_validation("denied", elapsed_ms)
            return False, None, "Access denied by User Service gRPC Interceptor"
        record_grpc_validation("error", elapsed_ms)
        return False, None, f"User Service gRPC error: {err.details()}"

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    if not response.exists:
        record_grpc_validation("not_found", elapsed_ms)
        return False, None, f"User with id {user_id} does not exist in User Service"

    record_grpc_validation("success", elapsed_ms)
    return True, response.role, None
