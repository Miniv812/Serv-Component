def test_account_and_expense_deduction_flow(client, auth_users):
    u1_id = auth_users["user1"]["id"]
    u1_headers = auth_users["user1"]["headers"]
    u2_headers = auth_users["user2"]["headers"]
    adm_headers = auth_users["admin"]["headers"]

    cat_res = client.post(
        "/category/global",
        headers=adm_headers,
        json={"name": "Coffee"},
    )
    category_id = cat_res.get_json()["id"]

    acc_res = client.post(
        "/account",
        headers=u1_headers,
        json={"balance": 200.0},
    )
    assert acc_res.status_code == 201
    account_id = acc_res.get_json()["id"]

    dep_res = client.post(
        f"/account/{account_id}/deposit",
        headers=u1_headers,
        json={"amount": 50.0},
    )
    assert dep_res.status_code == 200
    assert dep_res.get_json()["balance"] == 250.0

    rec_res = client.post(
        "/record",
        headers=u1_headers,
        json={"category_id": category_id, "amount": 75.5},
    )
    assert rec_res.status_code == 201
    assert rec_res.get_json()["remaining_balance"] == 174.5

    insufficient_res = client.post(
        "/record",
        headers=u1_headers,
        json={"category_id": category_id, "amount": 5000.0},
    )
    assert insufficient_res.status_code == 400
    assert insufficient_res.get_json()["error"] == "insufficient_funds"

    forbidden_filter = client.get(
        f"/record?user_id={u1_id}",
        headers=u2_headers,
    )
    assert forbidden_filter.status_code == 403
