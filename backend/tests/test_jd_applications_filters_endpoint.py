import io


def _seed_candidates_and_applications(client):
    jd = client.post(
        "/api/jds", json={"title": "Backend Engineer", "text": "Python Flask SQL"}
    ).get_json()

    candidate_one = client.post(
        "/api/candidates/upload",
        data={
            "resume": (io.BytesIO(b"resume1"), "candidate1.txt"),
            "full_name": "Candidate One",
            "extracted_text": "python flask sql 5 years",
            "profile_json": '{"skills": ["python", "flask", "sql"], "years_experience": 5}',
        },
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    candidate_two = client.post(
        "/api/candidates/upload",
        data={
            "resume": (io.BytesIO(b"resume2"), "candidate2.txt"),
            "full_name": "Candidate Two",
            "extracted_text": "python react 2 years",
            "profile_json": '{"skills": ["python", "react"], "years_experience": 2}',
        },
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    app_one = client.post(
        "/api/applications",
        json={"candidate_id": candidate_one["id"], "jd_id": jd["id"], "total_score": 88.0},
    ).get_json()
    app_two = client.post(
        "/api/applications",
        json={"candidate_id": candidate_two["id"], "jd_id": jd["id"], "total_score": 61.0},
    ).get_json()

    client.patch(
        f"/api/applications/{app_one['id']}/status",
        json={"status": "shortlisted", "reviewed_by": "admin"},
    )
    client.patch(
        f"/api/applications/{app_two['id']}/status",
        json={"status": "reviewed", "reviewed_by": "admin"},
    )

    return jd, app_one, app_two


def test_filter_by_min_score(client):
    jd, app_one, app_two = _seed_candidates_and_applications(client)

    response = client.get(f"/api/jds/{jd['id']}/applications?min_score=80")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == app_one["id"]


def test_filter_by_skills(client):
    jd, app_one, app_two = _seed_candidates_and_applications(client)

    response = client.get(f"/api/jds/{jd['id']}/applications?skills=python,flask")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == app_one["id"]


def test_filter_by_min_experience(client):
    jd, app_one, app_two = _seed_candidates_and_applications(client)

    response = client.get(f"/api/jds/{jd['id']}/applications?min_experience=3")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == app_one["id"]


def test_filter_by_status(client):
    jd, app_one, app_two = _seed_candidates_and_applications(client)

    response = client.get(f"/api/jds/{jd['id']}/applications?status=shortlisted")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == app_one["id"]


def test_filter_validation_error(client):
    jd, _, _ = _seed_candidates_and_applications(client)

    response = client.get(f"/api/jds/{jd['id']}/applications?min_experience=abc")

    assert response.status_code == 400
    assert "error" in response.get_json()
