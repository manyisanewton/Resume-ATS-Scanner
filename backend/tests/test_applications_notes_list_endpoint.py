import io


def test_list_application_notes_success(client):
    jd = client.post("/api/jds", json={"title": "Product Manager", "text": "Roadmap"}).get_json()
    candidate = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"resume"), "candidate.txt")},
        content_type="multipart/form-data",
    ).get_json()["candidate"]
    application = client.post(
        "/api/applications",
        json={"candidate_id": candidate["id"], "jd_id": jd["id"]},
    ).get_json()

    client.post(
        f"/api/applications/{application['id']}/notes",
        json={"author_name": "Recruiter One", "note_text": "Good fit"},
    )
    client.post(
        f"/api/applications/{application['id']}/notes",
        json={"author_name": "Recruiter Two", "note_text": "Needs deeper SQL"},
    )

    response = client.get(f"/api/applications/{application['id']}/notes")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2


def test_list_application_notes_not_found(client):
    response = client.get("/api/applications/9999/notes")

    assert response.status_code == 404
    assert "error" in response.get_json()
