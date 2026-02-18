def test_swagger_ui_is_available(client):
    response = client.get('/api/docs/')

    assert response.status_code == 200


def test_swagger_spec_is_available(client):
    response = client.get('/apispec_1.json')

    assert response.status_code == 200
    body = response.get_json()
    assert body["info"]["title"].startswith("Resume ATS Scanner API")
