import csv
import io


def test_shortlist_export_csv_returns_only_shortlisted_candidates(client):
    jd = client.post(
        "/api/jds", json={"title": "Backend Role", "text": "Python Flask"}
    ).get_json()

    shortlisted_candidate = client.post(
        "/api/candidates/upload",
        data={
            "resume": (io.BytesIO(b"resume1"), "candidate1.txt"),
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "1111111111",
        },
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    rejected_candidate = client.post(
        "/api/candidates/upload",
        data={
            "resume": (io.BytesIO(b"resume2"), "candidate2.txt"),
            "full_name": "John Doe",
            "email": "john@example.com",
        },
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    shortlisted_application = client.post(
        "/api/applications",
        json={
            "candidate_id": shortlisted_candidate["id"],
            "jd_id": jd["id"],
            "total_score": 87.5,
        },
    ).get_json()
    rejected_application = client.post(
        "/api/applications",
        json={
            "candidate_id": rejected_candidate["id"],
            "jd_id": jd["id"],
            "total_score": 32.0,
        },
    ).get_json()

    client.patch(
        f"/api/applications/{shortlisted_application['id']}/status",
        json={"status": "shortlisted", "reviewed_by": "admin"},
    )
    client.patch(
        f"/api/applications/{rejected_application['id']}/status",
        json={"status": "rejected", "reviewed_by": "admin"},
    )

    response = client.get(f"/api/jds/{jd['id']}/shortlist/export.csv")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "attachment;" in response.headers["Content-Disposition"]

    content = response.get_data(as_text=True)
    rows = list(csv.DictReader(io.StringIO(content)))

    assert len(rows) == 1
    assert rows[0]["candidate_id"] == str(shortlisted_candidate["id"])
    assert rows[0]["full_name"] == "Jane Doe"
    assert rows[0]["status"] == "shortlisted"


def test_shortlist_export_requires_auth(anonymous_client):
    response = anonymous_client.get("/api/jds/1/shortlist/export.csv")

    assert response.status_code == 401
    assert "error" in response.get_json()
