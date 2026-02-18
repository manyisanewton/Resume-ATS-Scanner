import io
import os


def test_process_candidate_success(client):
    upload = client.post(
        "/api/candidates/upload",
        data={
            "resume": (
                io.BytesIO(b"Python Flask PostgreSQL 5 years Bachelor"),
                "resume.txt",
            )
        },
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    response = client.post(f"/api/candidates/{upload['id']}/process", json={})

    assert response.status_code == 200
    body = response.get_json()
    assert body["job"]["status"] == "completed"
    assert "python" in body["candidate"]["profile_json"]["skills"]
    assert body["candidate"]["profile_json"]["years_experience"] == 5


def test_process_candidate_not_found(client):
    response = client.post("/api/candidates/99999/process", json={})

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_process_candidate_failure_when_file_missing(client):
    upload = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"resume body"), "resume.txt")},
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    os.remove(upload["resume_path"])

    response = client.post(f"/api/candidates/{upload['id']}/process", json={})

    assert response.status_code == 500
    body = response.get_json()
    assert body["job"]["status"] == "failed"
