from flask import Blueprint, jsonify, request
from flasgger import swag_from

from app.auth import require_auth
from app.extensions import db
from app.models.job_description import JobDescription

jd_bp = Blueprint("job_descriptions", __name__)


@jd_bp.post("/jds")
@require_auth(roles={"admin", "recruiter"})
@swag_from({
    "tags": ["Job Descriptions"],
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["title", "text"],
                    "properties": {
                        "title": {"type": "string"},
                        "department": {"type": "string"},
                        "level": {"type": "string"},
                        "location": {"type": "string"},
                        "text": {"type": "string"},
                    },
                }
            }
        },
    },
    "responses": {
        201: {"description": "JD created"},
        400: {"description": "Invalid payload"},
    },
})
def create_jd():
    payload = request.get_json(silent=True) or {}
    if not payload.get("title") or not payload.get("text"):
        return jsonify({"error": "title and text are required"}), 400

    jd = JobDescription(
        title=payload["title"].strip(),
        department=payload.get("department"),
        level=payload.get("level"),
        location=payload.get("location"),
        text=payload["text"].strip(),
    )
    db.session.add(jd)
    db.session.commit()
    return jsonify(jd.to_dict()), 201


@jd_bp.get("/jds")
@require_auth(roles={"admin", "recruiter"})
@swag_from({
    "tags": ["Job Descriptions"],
    "responses": {200: {"description": "List JDs"}},
})
def list_jds():
    items = JobDescription.query.order_by(JobDescription.created_at.desc()).all()
    return jsonify([item.to_dict() for item in items]), 200


@jd_bp.get("/jds/<int:jd_id>")
@require_auth(roles={"admin", "recruiter"})
@swag_from({
    "tags": ["Job Descriptions"],
    "parameters": [{"name": "jd_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
    "responses": {200: {"description": "JD detail"}, 404: {"description": "Not found"}},
})
def get_jd(jd_id: int):
    jd = db.session.get(JobDescription, jd_id)
    if jd is None:
        return jsonify({"error": "job description not found"}), 404
    return jsonify(jd.to_dict()), 200
