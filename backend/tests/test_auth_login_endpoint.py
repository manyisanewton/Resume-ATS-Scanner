def test_login_success(anonymous_client):
    anonymous_client.post(
        "/api/auth/bootstrap-admin",
        json={"username": "adminlogin", "password": "StrongPass123"},
    )

    response = anonymous_client.post(
        "/api/auth/login",
        json={"username": "adminlogin", "password": "StrongPass123"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert "access_token" in body
    assert body["user"]["username"] == "adminlogin"


def test_login_invalid_credentials(anonymous_client):
    anonymous_client.post(
        "/api/auth/bootstrap-admin",
        json={"username": "adminlogin", "password": "StrongPass123"},
    )

    response = anonymous_client.post(
        "/api/auth/login",
        json={"username": "adminlogin", "password": "wrong"},
    )

    assert response.status_code == 401
    assert "error" in response.get_json()
