import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///resume_ats_dev.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "logs/audit.log")
    TOKEN_MAX_AGE_SECONDS = int(os.getenv("TOKEN_MAX_AGE_SECONDS", "28800"))
    SWAGGER = {
        "title": "Resume ATS Scanner API",
        "uiversion": 3,
        "openapi": "3.0.2",
        "specs_route": "/api/docs/",
    }
