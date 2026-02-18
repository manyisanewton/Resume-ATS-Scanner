from flask import Flask

from .config import Config
from .extensions import db, migrate, swagger
from .middleware.audit import init_audit_middleware
from .routes.auth import auth_bp, users_bp
from .routes.health import health_bp
from .routes.job_descriptions import jd_bp
from .routes.candidates import candidates_bp
from .routes.applications import applications_bp
from .routes.processing_jobs import processing_jobs_bp


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    swagger.init_app(app)
    init_audit_middleware(app)

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(jd_bp, url_prefix="/api")
    app.register_blueprint(candidates_bp, url_prefix="/api")
    app.register_blueprint(applications_bp, url_prefix="/api")
    app.register_blueprint(processing_jobs_bp, url_prefix="/api")

    return app
