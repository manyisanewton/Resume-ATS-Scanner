def test_jd_endpoints_require_token(anonymous_client):
    response = anonymous_client.get("/api/jds")

    assert response.status_code == 401
    assert "error" in response.get_json()
