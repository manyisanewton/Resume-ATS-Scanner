def test_get_jd_success(client):
    created = client.post("/api/jds", json={"title": "JD 1", "text": "Skill A"}).get_json()

    response = client.get(f"/api/jds/{created['id']}")

    assert response.status_code == 200
    assert response.get_json()["id"] == created["id"]


def test_get_jd_not_found(client):
    response = client.get("/api/jds/9999")

    assert response.status_code == 404
    assert "error" in response.get_json()
