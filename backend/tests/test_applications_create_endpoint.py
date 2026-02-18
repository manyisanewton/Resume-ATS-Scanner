import io


def test_create_application_success(client):
    jd = client.post("/api/jds", json={"title": "Python Engineer", "text": "Flask PostgreSQL"}).get_json()
    candidate = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"resume body"), "candidate.txt")},
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    response = client.post(
        "/api/applications",
        json={
            "candidate_id": candidate["id"],
            "jd_id": jd["id"],
            "total_score": 78.5,
            "score_breakdown_json": {"skills": 80, "experience": 70},
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["candidate_id"] == candidate["id"]
    assert body["jd_id"] == jd["id"]


def test_create_application_validation_error(client):
    response = client.post("/api/applications", json={})

    assert response.status_code == 400
    assert "error" in response.get_json()
