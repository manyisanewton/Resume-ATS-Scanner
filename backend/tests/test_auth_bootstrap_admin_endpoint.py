def test_bootstrap_admin_success(anonymous_client):
    response = anonymous_client.post(
        "/api/auth/bootstrap-admin",
        json={"username": "firstadmin", "password": "StrongPass123"},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["user"]["username"] == "firstadmin"
    assert body["user"]["role"] == "admin"


def test_bootstrap_admin_rejects_when_admin_exists(anonymous_client):
    anonymous_client.post(
        "/api/auth/bootstrap-admin",
        json={"username": "firstadmin", "password": "StrongPass123"},
    )

    response = anonymous_client.post(
        "/api/auth/bootstrap-admin",
        json={"username": "another", "password": "StrongPass123"},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()
