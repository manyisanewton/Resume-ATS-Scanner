def test_users_me_success(client):
    response = client.get("/api/users/me")

    assert response.status_code == 200
    body = response.get_json()
    assert body["username"] == "admin"
    assert body["role"] == "admin"


def test_users_me_unauthorized_without_token(anonymous_client):
    response = anonymous_client.get("/api/users/me")

    assert response.status_code == 401
    assert "error" in response.get_json()
