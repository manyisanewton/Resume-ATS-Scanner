import io


def test_update_application_status_success(client):
    jd = client.post("/api/jds", json={"title": "QA Engineer", "text": "Testing"}).get_json()
    candidate = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"resume"), "candidate.txt")},
        content_type="multipart/form-data",
    ).get_json()["candidate"]
    application = client.post(
        "/api/applications",
        json={"candidate_id": candidate["id"], "jd_id": jd["id"]},
    ).get_json()

    response = client.patch(
        f"/api/applications/{application['id']}/status",
        json={"status": "shortlisted", "reviewed_by": "recruiter@company.com"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "shortlisted"
    assert body["reviewed_by"] == "recruiter@company.com"


def test_update_application_status_invalid_status(client):
    jd = client.post("/api/jds", json={"title": "QA Engineer", "text": "Testing"}).get_json()
    candidate = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"resume"), "candidate.txt")},
        content_type="multipart/form-data",
    ).get_json()["candidate"]
    application = client.post(
        "/api/applications",
        json={"candidate_id": candidate["id"], "jd_id": jd["id"]},
    ).get_json()

    response = client.patch(
        f"/api/applications/{application['id']}/status",
        json={"status": "unknown-status"},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()
