import io


def test_get_candidate_success(client):
    upload_resp = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"resume body"), "candidate.txt")},
        content_type="multipart/form-data",
    )
    candidate_id = upload_resp.get_json()["candidate"]["id"]

    response = client.get(f"/api/candidates/{candidate_id}")

    assert response.status_code == 200
    assert response.get_json()["id"] == candidate_id


def test_get_candidate_not_found(client):
    response = client.get("/api/candidates/9999")

    assert response.status_code == 404
    assert "error" in response.get_json()
