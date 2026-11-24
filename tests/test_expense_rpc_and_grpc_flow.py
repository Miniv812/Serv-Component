def test_cross_service_grpc_verification_and_account_flow(
    user_client,
    expense_client,
    auth_users,
):
    u1_headers = auth_users["user1"]["headers"]
    u2_id = auth_users["user2"]["id"]
    u2_headers = auth_users["user2"]["headers"]
    adm_headers = auth_users["admin"]["headers"]

    # 1. Адміністратор створює глобальну категорію в Expense Service
    cat_res = expense_client.post(
        "/category/global",
        headers=adm_headers,
        json={"name": "Транспорт"},
    )
    assert cat_res.status_code == 201
    category_id = cat_res.get_json()["id"]

    # 2. User1 створює рахунок (Expense Service перевіряє користувача через gRPC)
    acc_res = expense_client.post(
        "/account",
        headers=u1_headers,
        json={"balance": 300.0},
    )
    assert acc_res.status_code == 201
    account_id = acc_res.get_json()["id"]

    # 3. Створення витрати через REST зі списанням з рахунку
    rec_res = expense_client.post(
        "/record",
        headers=u1_headers,
        json={"category_id": category_id, "amount": 50.0},
    )
    assert rec_res.status_code == 201
    assert rec_res.get_json()["remaining_balance"] == 250.0

    # 4. Видаляємо User2 в User Service -> перевіряємо, що gRPC відхилить запит
    del_res = user_client.delete(f"/user/{u2_id}", headers=adm_headers)
    assert del_res.status_code == 204

    blocked_acc = expense_client.post(
        "/account",
        headers=u2_headers,
        json={"balance": 100.0},
    )
    assert blocked_acc.status_code == 403
    assert "does not exist" in blocked_acc.get_json()["message"]

    # Перевірка ізоляції account_id (щоб не було невикористаної змінної)
    get_acc = expense_client.get(f"/account/{account_id}", headers=u1_headers)
    assert get_acc.status_code == 200


def test_json_rpc_single_and_batch_requests(expense_client, auth_users):
    u1_id = auth_users["user1"]["id"]
    u1_headers = auth_users["user1"]["headers"]
    adm_headers = auth_users["admin"]["headers"]

    cat_res = expense_client.post(
        "/category/global",
        headers=adm_headers,
        json={"name": "Продукти"},
    )
    category_id = cat_res.get_json()["id"]

    acc_res = expense_client.post(
        "/account",
        headers=u1_headers,
        json={"balance": 500.0},
    )
    assert acc_res.status_code == 201

    # 1. Single JSON-RPC 2.0 запит
    single_payload = {
        "jsonrpc": "2.0",
        "method": "create_record",
        "params": {"user_id": u1_id, "category_id": category_id, "amount": 100.0},
        "id": 1,
    }
    single_res = expense_client.post("/rpc", headers=u1_headers, json=single_payload)
    assert single_res.status_code == 200
    single_data = single_res.get_json()
    assert single_data["jsonrpc"] == "2.0"
    assert single_data["id"] == 1
    assert single_data["result"]["status"] == "created"
    assert single_data["result"]["remaining_balance"] == 400.0

    # 2. Batch JSON-RPC 2.0 запит (масив із кількох викликів)
    batch_payload = [
        {
            "jsonrpc": "2.0",
            "method": "create_record",
            "params": {"user_id": u1_id, "category_id": category_id, "amount": 45.5},
            "id": 2,
        },
        {
            "jsonrpc": "2.0",
            "method": "create_record",
            "params": {"user_id": u1_id, "category_id": category_id, "amount": 54.5},
            "id": 3,
        },
        {
            "jsonrpc": "2.0",
            "method": "unknown_method",
            "params": {},
            "id": 4,
        },
    ]
    batch_res = expense_client.post("/rpc", headers=u1_headers, json=batch_payload)
    assert batch_res.status_code == 200
    batch_data = batch_res.get_json()
    assert isinstance(batch_data, list)
    assert len(batch_data) == 3

    assert batch_data[0]["id"] == 2
    assert batch_data[0]["result"]["remaining_balance"] == 354.5

    assert batch_data[1]["id"] == 3
    assert batch_data[1]["result"]["remaining_balance"] == 300.0

    assert batch_data[2]["id"] == 4
    assert batch_data[2]["error"]["code"] == -32601
