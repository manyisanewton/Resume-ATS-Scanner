from pathlib import Path


def test_request_id_header_is_present(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_audit_log_file_is_written(client, app):
    response = client.get("/api/health")
    assert response.status_code == 200

    configured_path = Path(app.config["AUDIT_LOG_PATH"])
    if not configured_path.is_absolute():
        configured_path = Path(app.root_path).parent / configured_path

    assert configured_path.exists()
    content = configured_path.read_text(encoding="utf-8", errors="ignore")
    assert '"path": "/api/health"' in content
