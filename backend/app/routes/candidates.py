from datetime import UTC, datetime
import json
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request
from flasgger import swag_from
from werkzeug.utils import secure_filename

from app.auth import require_auth
from app.extensions import db
from app.models.candidate import Candidate
from app.models.processing_job import ProcessingJob
from app.services.resume_parser import extract_profile_from_text, parse_resume_file

candidates_bp = Blueprint("candidates", __name__)


@candidates_bp.post("/candidates/upload")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Candidates"],
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "resume": {"type": "string", "format": "binary"},
                            "full_name": {"type": "string"},
                            "email": {"type": "string"},
                            "phone": {"type": "string"},
                            "extracted_text": {"type": "string"},
                            "profile_json": {"type": "string", "example": "{\"skills\": [\"python\"], \"years_experience\": 4}"},
                        },
                        "required": ["resume"],
                    }
                }
            },
        },
        "responses": {
            201: {"description": "Candidate created and queued for processing"},
            400: {"description": "Missing resume"},
        },
    }
)
def upload_candidate_resume():
    if "resume" not in request.files:
        return jsonify({"error": "resume file is required"}), 400

    resume = request.files["resume"]
    if not resume.filename:
        return jsonify({"error": "resume filename is required"}), 400

    configured_upload = current_app.config.get("UPLOAD_DIR", "uploads")
    upload_root = Path(configured_upload)
    if not upload_root.is_absolute():
        upload_root = Path(current_app.root_path).parent / upload_root
    upload_root.mkdir(parents=True, exist_ok=True)

    safe_name = secure_filename(resume.filename)
    unique_name = f"{uuid4().hex}_{safe_name}"
    output_path = upload_root / unique_name
    resume.save(output_path)

    profile_json = None
    raw_profile = request.form.get("profile_json")
    if raw_profile:
        try:
            parsed = json.loads(raw_profile)
        except json.JSONDecodeError:
            return jsonify({"error": "profile_json must be valid JSON"}), 400
        if not isinstance(parsed, dict):
            return jsonify({"error": "profile_json must be a JSON object"}), 400
        profile_json = parsed

    candidate = Candidate(
        full_name=(request.form.get("full_name") or None),
        email=(request.form.get("email") or None),
        phone=(request.form.get("phone") or None),
        resume_filename=safe_name,
        resume_path=str(output_path),
        extracted_text=(request.form.get("extracted_text") or None),
        profile_json=profile_json,
    )
    db.session.add(candidate)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "resume accepted",
                "candidate": candidate.to_dict(),
                "status": "queued",
            }
        ),
        201,
    )


@candidates_bp.get("/candidates/<int:candidate_id>")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Candidates"],
        "parameters": [
            {
                "name": "candidate_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        "responses": {200: {"description": "Candidate detail"}, 404: {"description": "Not found"}},
    }
)
def get_candidate(candidate_id: int):
    candidate = db.session.get(Candidate, candidate_id)
    if candidate is None:
        return jsonify({"error": "candidate not found"}), 404
    return jsonify(candidate.to_dict()), 200


@candidates_bp.post("/candidates/<int:candidate_id>/process")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Candidates"],
        "parameters": [
            {
                "name": "candidate_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        "requestBody": {
            "required": False,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"force_reprocess": {"type": "boolean"}},
                    }
                }
            },
        },
        "responses": {
            200: {"description": "Candidate processed"},
            404: {"description": "Candidate not found"},
            500: {"description": "Processing failed"},
        },
    }
)
def process_candidate_resume(candidate_id: int):
    candidate = db.session.get(Candidate, candidate_id)
    if candidate is None:
        return jsonify({"error": "candidate not found"}), 404

    payload = request.get_json(silent=True) or {}
    force_reprocess = bool(payload.get("force_reprocess", False))

    job = ProcessingJob(entity_type="candidate", entity_id=candidate_id, status="queued")
    db.session.add(job)
    db.session.commit()

    try:
        job.status = "processing"
        job.started_at = datetime.now(UTC)
        db.session.commit()

        extracted_text = parse_resume_file(candidate.resume_path)
        profile_json = extract_profile_from_text(extracted_text)

        if force_reprocess or not candidate.extracted_text:
            candidate.extracted_text = extracted_text
        if force_reprocess or not candidate.profile_json:
            candidate.profile_json = profile_json

        job.status = "completed"
        job.completed_at = datetime.now(UTC)
        db.session.commit()
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.completed_at = datetime.now(UTC)
        db.session.commit()
        return jsonify({"error": "processing failed", "job": job.to_dict()}), 500

    return (
        jsonify(
            {
                "message": "candidate processed",
                "job": job.to_dict(),
                "candidate": candidate.to_dict(),
            }
        ),
        200,
    )
