import io


def test_upload_resume_success(client):
    response = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"sample resume data"), "resume.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["status"] == "queued"
    assert body["candidate"]["resume_filename"] == "resume.txt"


def test_upload_resume_missing_file(client):
    response = client.post(
        "/api/candidates/upload",
        data={},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_upload_resume_with_invalid_profile_json(client):
    response = client.post(
        "/api/candidates/upload",
        data={
            "resume": (io.BytesIO(b"sample resume data"), "resume.txt"),
            "profile_json": "{\"skills\":[python]}",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "error" in response.get_json()
