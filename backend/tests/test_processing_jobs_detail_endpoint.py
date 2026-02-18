import io


def test_get_processing_job_success(client):
    upload = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"Python 2 years"), "resume.txt")},
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    process_response = client.post(f"/api/candidates/{upload['id']}/process", json={})
    job_id = process_response.get_json()["job"]["id"]

    response = client.get(f"/api/processing-jobs/{job_id}")

    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == job_id
    assert body["entity_type"] == "candidate"


def test_get_processing_job_not_found(client):
    response = client.get("/api/processing-jobs/99999")

    assert response.status_code == 404
    assert "error" in response.get_json()
