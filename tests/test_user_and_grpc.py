import grpc
import pytest
from freezegun import freeze_time

from proto import auth_pb2, auth_pb2_grpc
from user_app.extensions import db as user_db
from user_app.models import UserModel


@freeze_time("2026-11-24 12:00:00")
def test_user_service_healthcheck(user_client):
    live_res = user_client.get("/healthz/live")
    assert live_res.status_code == 200
    live_data = live_res.get_json()
    assert live_data["service"] == "user-service"
    assert live_data["timestamp"].startswith("2026-11-24T12:00:00")

    ready_res = user_client.get("/healthz/ready")
    assert ready_res.status_code == 200
    assert ready_res.get_json()["database"] == "connected"


def test_register_login_and_grpc_validate_token(
    user_client,
    user_app,
    grpc_server_addr,
):
    reg_res = user_client.post(
        "/register",
        json={
            "username": "student_kpi",
            "name": "Владислав",
            "password": "StrongPassword2026",
        },
    )
    assert reg_res.status_code == 201
    user_id = reg_res.get_json()["id"]

    with user_app.app_context():
        user = user_db.session.get(UserModel, user_id)
        assert user.password_hash.startswith("$argon2")

    login_res = user_client.post(
        "/login",
        json={"username": "student_kpi", "password": "StrongPassword2026"},
    )
    assert login_res.status_code == 200
    token = login_res.get_json()["access_token"]

    with grpc.insecure_channel(grpc_server_addr) as channel:
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        grpc_res = stub.ValidateToken(auth_pb2.ValidateTokenRequest(token=token))
        assert grpc_res.is_valid is True
        assert grpc_res.user_id == str(user_id)
        assert list(grpc_res.roles) == ["user"]


def test_grpc_rbac_server_interceptor_blocks_missing_metadata(
    grpc_server_addr,
    auth_users,
):
    u1_id = auth_users["user1"]["id"]
    u1_token = auth_users["user1"]["headers"]["Authorization"]

    with grpc.insecure_channel(grpc_server_addr) as channel:
        stub = auth_pb2_grpc.AuthServiceStub(channel)

        # Виклик без gRPC Metadata має бути заблокований RBACServerInterceptor
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.ValidateUser(auth_pb2.UserRequest(user_id=u1_id))
        assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED

        # Виклик із валідним Bearer-токеном у Metadata має пройти успішно
        valid_res = stub.ValidateUser(
            auth_pb2.UserRequest(user_id=u1_id),
            metadata=[("authorization", u1_token)],
        )
        assert valid_res.exists is True
        assert valid_res.role == "user"
