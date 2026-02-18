import io


def test_create_application_note_success(client):
    jd = client.post("/api/jds", json={"title": "DevOps", "text": "AWS"}).get_json()
    candidate = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"resume"), "candidate.txt")},
        content_type="multipart/form-data",
    ).get_json()["candidate"]
    application = client.post(
        "/api/applications",
        json={"candidate_id": candidate["id"], "jd_id": jd["id"]},
    ).get_json()

    response = client.post(
        f"/api/applications/{application['id']}/notes",
        json={"author_name": "Recruiter One", "note_text": "Strong cloud background."},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["author_name"] == "Recruiter One"


def test_create_application_note_validation_error(client):
    jd = client.post("/api/jds", json={"title": "DevOps", "text": "AWS"}).get_json()
    candidate = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"resume"), "candidate.txt")},
        content_type="multipart/form-data",
    ).get_json()["candidate"]
    application = client.post(
        "/api/applications",
        json={"candidate_id": candidate["id"], "jd_id": jd["id"]},
    ).get_json()

    response = client.post(
        f"/api/applications/{application['id']}/notes",
        json={"author_name": "Recruiter One"},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()
