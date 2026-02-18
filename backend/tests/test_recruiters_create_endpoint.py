def test_create_recruiter_success_for_admin(client):
    response = client.post(
        "/api/users/recruiters",
        json={"username": "recruiter-new", "password": "RecruiterPass123"},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["user"]["username"] == "recruiter-new"
    assert body["user"]["role"] == "recruiter"


def test_create_recruiter_forbidden_for_recruiter_role(
    anonymous_client, recruiter_auth_header
):
    response = anonymous_client.post(
        "/api/users/recruiters",
        json={"username": "cannot-create", "password": "RecruiterPass123"},
        headers={"Authorization": recruiter_auth_header},
    )

    assert response.status_code == 403
    assert "error" in response.get_json()
