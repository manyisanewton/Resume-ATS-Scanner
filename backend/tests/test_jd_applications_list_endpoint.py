import io


def test_list_applications_for_jd_sorted_by_score_desc(client):
    jd = client.post("/api/jds", json={"title": "Data Engineer", "text": "Python SQL"}).get_json()

    candidate_one = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"resume1"), "candidate1.txt")},
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    candidate_two = client.post(
        "/api/candidates/upload",
        data={"resume": (io.BytesIO(b"resume2"), "candidate2.txt")},
        content_type="multipart/form-data",
    ).get_json()["candidate"]

    client.post(
        "/api/applications",
        json={"candidate_id": candidate_one["id"], "jd_id": jd["id"], "total_score": 55.0},
    )
    client.post(
        "/api/applications",
        json={"candidate_id": candidate_two["id"], "jd_id": jd["id"], "total_score": 91.0},
    )

    response = client.get(f"/api/jds/{jd['id']}/applications?sort=score_desc")

    assert response.status_code == 200
    body = response.get_json()
    assert body[0]["total_score"] == 91.0
    assert body[1]["total_score"] == 55.0


def test_list_applications_for_missing_jd(client):
    response = client.get("/api/jds/9999/applications")

    assert response.status_code == 404
    assert "error" in response.get_json()
