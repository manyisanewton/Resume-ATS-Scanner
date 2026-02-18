def test_list_jds_returns_array(client):
    client.post("/api/jds", json={"title": "JD 1", "text": "Skill A"})
    client.post("/api/jds", json={"title": "JD 2", "text": "Skill B"})

    response = client.get("/api/jds")

    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, list)
    assert len(body) == 2
