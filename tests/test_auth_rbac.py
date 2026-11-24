from app.extensions import db
from app.models import UserModel


def test_register_and_login_flow(client, app):
    reg_res = client.post(
        "/register",
        json={
            "username": "new_student",
            "name": "Тарас",
            "password": "StrongPassword2026",
        },
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.get_json()
    assert reg_data["username"] == "new_student"
    assert reg_data["role"] == "user"
    assert "password_hash" not in reg_data

    with app.app_context():
        user = db.session.get(UserModel, reg_data["id"])
        assert user.password_hash.startswith("$argon2")

    login_res = client.post(
        "/login",
        json={"username": "new_student", "password": "StrongPassword2026"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.get_json()


def test_unauthorized_access_returns_401(client):
    res = client.get("/users")
    assert res.status_code == 401
    assert res.get_json()["error"] == "unauthorized"


def test_rbac_user_cannot_access_admin_endpoints(client, auth_users):
    u1_headers = auth_users["user1"]["headers"]

    res_users = client.get("/users", headers=u1_headers)
    assert res_users.status_code == 403
    assert res_users.get_json()["error"] == "forbidden"

    res_global_cat = client.post(
        "/category/global",
        headers=u1_headers,
        json={"name": "Global Food"},
    )
    assert res_global_cat.status_code == 403


def test_rbac_user_isolation_returns_404(client, auth_users):
    u1_headers = auth_users["user1"]["headers"]
    u2_id = auth_users["user2"]["id"]

    res = client.get(f"/user/{u2_id}", headers=u1_headers)
    assert res.status_code == 404


def test_rbac_auditor_is_read_only(client, auth_users):
    aud_headers = auth_users["auditor"]["headers"]

    res_list = client.get("/users", headers=aud_headers)
    assert res_list.status_code == 200
    assert len(res_list.get_json()) == 4

    res_create_cat = client.post(
        "/category",
        headers=aud_headers,
        json={"name": "Blocked"},
    )
    assert res_create_cat.status_code == 403


def test_rbac_admin_full_access(client, auth_users):
    adm_headers = auth_users["admin"]["headers"]
    u2_id = auth_users["user2"]["id"]

    cat_res = client.post(
        "/category/global",
        headers=adm_headers,
        json={"name": "Transport"},
    )
    assert cat_res.status_code == 201
    assert cat_res.get_json()["is_global"] is True

    del_res = client.delete(f"/user/{u2_id}", headers=adm_headers)
    assert del_res.status_code == 204
