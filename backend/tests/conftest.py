import os
import shutil
import tempfile

import pytest

from app import create_app
from app.extensions import db
from app.models.user import User
from app.services.auth import generate_access_token


@pytest.fixture
def app():
    fd, db_path = tempfile.mkstemp(prefix="resume_ats_test_", suffix=".db")
    os.close(fd)
    upload_dir = tempfile.mkdtemp(prefix="resume_ats_uploads_")
    audit_dir = tempfile.mkdtemp(prefix="resume_ats_audit_")
    audit_log_path = os.path.join(audit_dir, "audit.log")

    class TestConfig:
        TESTING = True
        SECRET_KEY = "test-secret"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        UPLOAD_DIR = upload_dir
        AUDIT_LOG_PATH = audit_log_path
        TOKEN_MAX_AGE_SECONDS = 28800
        SWAGGER = {
            "title": "Resume ATS Scanner API (Test)",
            "uiversion": 3,
            "openapi": "3.0.2",
            "specs_route": "/api/docs/",
        }

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()
    os.remove(db_path)
    shutil.rmtree(upload_dir)
    shutil.rmtree(audit_dir)


@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User.query.filter_by(username="admin").first()
        if user is None:
            user = User(username="admin", role="admin", is_active=True)
            user.set_password("admin123")
            db.session.add(user)
            db.session.commit()
        return user.to_dict()


@pytest.fixture
def recruiter_user(app):
    with app.app_context():
        user = User.query.filter_by(username="recruiter").first()
        if user is None:
            user = User(username="recruiter", role="recruiter", is_active=True)
            user.set_password("recruiter123")
            db.session.add(user)
            db.session.commit()
        return user.to_dict()


@pytest.fixture
def admin_auth_header(app, admin_user):
    with app.app_context():
        token = generate_access_token(user_id=admin_user["id"], role="admin")
    return f"Bearer {token}"


@pytest.fixture
def recruiter_auth_header(app, recruiter_user):
    with app.app_context():
        token = generate_access_token(user_id=recruiter_user["id"], role="recruiter")
    return f"Bearer {token}"


@pytest.fixture
def client(app, admin_auth_header):
    client = app.test_client()
    client.environ_base["HTTP_AUTHORIZATION"] = admin_auth_header
    return client


@pytest.fixture
def anonymous_client(app):
    return app.test_client()
