import io


def test_score_endpoint_success_and_persists_score(client):
    jd = client.post(
        "/api/jds",
        json={
            "title": "Backend Engineer",
            "text": "Python Flask PostgreSQL 3 years Bachelor",
        },
    ).get_json()

    candidate = client.post(
        "/api/candidates/upload",
        data={
            "resume": (io.BytesIO(b"resume"), "candidate.txt"),
            "extracted_text": "Python Flask PostgreSQL 4 years Bachelor",
            "profile_json": '{"skills": ["python", "flask", "postgresql"], "years_experience": 4, "education": "bachelor"}',
        },
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    application = client.post(
        "/api/applications",
        json={"candidate_id": candidate["id"], "jd_id": jd["id"]},
    ).get_json()

    response = client.post(
        "/api/applications/score",
        json={"application_id": application["id"]},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["application_id"] == application["id"]
    assert isinstance(body["total_score"], float)
    assert body["total_score"] > 0
    assert "skills" in body["score_breakdown_json"]

    list_resp = client.get(f"/api/jds/{jd['id']}/applications").get_json()
    assert list_resp[0]["total_score"] == body["total_score"]


def test_score_endpoint_requires_application_id(client):
    response = client.post("/api/applications/score", json={})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_score_endpoint_not_found(client):
    response = client.post(
        "/api/applications/score",
        json={"application_id": 99999},
    )

    assert response.status_code == 404
    assert "error" in response.get_json()
