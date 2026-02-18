def test_create_jd_success(client):
    payload = {
        "title": "Backend Engineer",
        "text": "Python Flask PostgreSQL",
        "department": "Engineering",
    }

    response = client.post("/api/jds", json=payload)

    assert response.status_code == 201
    body = response.get_json()
    assert body["title"] == payload["title"]
    assert body["text"] == payload["text"]


def test_create_jd_validation_error(client):
    response = client.post("/api/jds", json={"title": "Missing text"})

    assert response.status_code == 400
    assert "error" in response.get_json()
