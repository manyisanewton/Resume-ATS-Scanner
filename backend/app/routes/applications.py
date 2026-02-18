import csv
import re
from io import StringIO
from datetime import UTC, datetime

from flask import Blueprint, Response, jsonify, request
from flasgger import swag_from

from app.auth import require_auth
from app.extensions import db
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.models.review_note import ReviewNote
from app.services.scoring import score_candidate_against_jd

applications_bp = Blueprint("applications", __name__)
VALID_STATUSES = {"new", "reviewed", "shortlisted", "rejected"}


def _extract_candidate_years(candidate: Candidate) -> int | None:
    if isinstance(candidate.profile_json, dict):
        years = candidate.profile_json.get("years_experience")
        if isinstance(years, (int, float)):
            return int(years)

    text = (candidate.extracted_text or "").lower()
    match = re.search(r"(\d{1,2})\s*\+?\s*years?", text)
    if match:
        return int(match.group(1))
    return None


def _candidate_matches_skills(candidate: Candidate, required_skills: set[str]) -> bool:
    if not required_skills:
        return True

    profile_skills = set()
    if isinstance(candidate.profile_json, dict):
        skills = candidate.profile_json.get("skills")
        if isinstance(skills, list):
            profile_skills = {str(skill).strip().lower() for skill in skills if str(skill).strip()}

    text_blob = (candidate.extracted_text or "").lower()
    for skill in required_skills:
        if skill in profile_skills or skill in text_blob:
            continue
        return False
    return True


@applications_bp.post("/applications")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Applications"],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["candidate_id", "jd_id"],
                        "properties": {
                            "candidate_id": {"type": "integer"},
                            "jd_id": {"type": "integer"},
                            "total_score": {"type": "number"},
                            "score_breakdown_json": {"type": "object"},
                        },
                    }
                }
            },
        },
        "responses": {201: {"description": "Application created"}, 400: {"description": "Invalid payload"}},
    }
)
def create_application():
    payload = request.get_json(silent=True) or {}
    candidate_id = payload.get("candidate_id")
    jd_id = payload.get("jd_id")

    if candidate_id is None or jd_id is None:
        return jsonify({"error": "candidate_id and jd_id are required"}), 400

    candidate = db.session.get(Candidate, candidate_id)
    jd = db.session.get(JobDescription, jd_id)
    if candidate is None or jd is None:
        return jsonify({"error": "candidate or job description not found"}), 400

    application = Application(
        candidate_id=candidate_id,
        jd_id=jd_id,
        total_score=payload.get("total_score"),
        score_breakdown_json=payload.get("score_breakdown_json"),
        status="new",
    )
    db.session.add(application)
    db.session.commit()
    return jsonify(application.to_dict()), 201


@applications_bp.get("/jds/<int:jd_id>/applications")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Applications"],
        "parameters": [
            {
                "name": "jd_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
            },
            {
                "name": "sort",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "example": "score_desc"},
            },
            {
                "name": "min_score",
                "in": "query",
                "required": False,
                "schema": {"type": "number", "example": 60},
            },
            {
                "name": "max_score",
                "in": "query",
                "required": False,
                "schema": {"type": "number", "example": 95},
            },
            {
                "name": "status",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "enum": ["new", "reviewed", "shortlisted", "rejected"]},
            },
            {
                "name": "skills",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "example": "python,flask"},
            },
            {
                "name": "min_experience",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "example": 3},
            },
        ],
        "responses": {
            200: {"description": "Applications for a JD"},
            400: {"description": "Invalid query filter"},
            404: {"description": "JD not found"},
        },
    }
)
def list_applications_for_jd(jd_id: int):
    jd = db.session.get(JobDescription, jd_id)
    if jd is None:
        return jsonify({"error": "job description not found"}), 404

    sort = request.args.get("sort", "score_desc")
    query = (
        db.session.query(Application, Candidate)
        .join(Candidate, Candidate.id == Application.candidate_id)
        .filter(Application.jd_id == jd_id)
    )

    min_score = request.args.get("min_score")
    max_score = request.args.get("max_score")
    if min_score is not None:
        try:
            min_score_value = float(min_score)
        except ValueError:
            return jsonify({"error": "min_score must be a number"}), 400
        query = query.filter(Application.total_score.isnot(None), Application.total_score >= min_score_value)

    if max_score is not None:
        try:
            max_score_value = float(max_score)
        except ValueError:
            return jsonify({"error": "max_score must be a number"}), 400
        query = query.filter(Application.total_score.isnot(None), Application.total_score <= max_score_value)

    status_filter = request.args.get("status")
    if status_filter:
        if status_filter not in VALID_STATUSES:
            return jsonify({"error": "invalid status value"}), 400
        query = query.filter(Application.status == status_filter)

    required_skills = {
        skill.strip().lower()
        for skill in (request.args.get("skills") or "").split(",")
        if skill.strip()
    }

    min_experience = request.args.get("min_experience")
    min_experience_value = None
    if min_experience is not None:
        try:
            min_experience_value = int(min_experience)
        except ValueError:
            return jsonify({"error": "min_experience must be an integer"}), 400

    rows = query.all()
    filtered_applications = []
    for application, candidate in rows:
        if not _candidate_matches_skills(candidate, required_skills):
            continue
        if min_experience_value is not None:
            candidate_years = _extract_candidate_years(candidate)
            if candidate_years is None or candidate_years < min_experience_value:
                continue
        filtered_applications.append(application)

    if sort == "score_asc":
        filtered_applications.sort(
            key=lambda item: (item.total_score is not None, item.total_score if item.total_score is not None else 0.0)
        )
    else:
        filtered_applications.sort(
            key=lambda item: (item.total_score is None, -(item.total_score if item.total_score is not None else 0.0))
        )

    return jsonify([item.to_dict() for item in filtered_applications]), 200


@applications_bp.get("/jds/<int:jd_id>/shortlist/export.csv")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Applications"],
        "parameters": [
            {
                "name": "jd_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        "responses": {200: {"description": "Shortlist export CSV"}, 404: {"description": "JD not found"}},
    }
)
def export_shortlist_csv(jd_id: int):
    jd = db.session.get(JobDescription, jd_id)
    if jd is None:
        return jsonify({"error": "job description not found"}), 404

    rows = (
        db.session.query(Application, Candidate)
        .join(Candidate, Candidate.id == Application.candidate_id)
        .filter(Application.jd_id == jd_id, Application.status == "shortlisted")
        .order_by(Application.total_score.desc())
        .all()
    )

    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(
        [
            "application_id",
            "candidate_id",
            "full_name",
            "email",
            "phone",
            "total_score",
            "status",
            "reviewed_by",
            "reviewed_at",
        ]
    )

    for application, candidate in rows:
        writer.writerow(
            [
                application.id,
                candidate.id,
                candidate.full_name or "",
                candidate.email or "",
                candidate.phone or "",
                application.total_score if application.total_score is not None else "",
                application.status,
                application.reviewed_by or "",
                application.reviewed_at.isoformat() if application.reviewed_at else "",
            ]
        )

    csv_data = out.getvalue()
    filename = f"jd_{jd_id}_shortlist.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'},
    )


@applications_bp.patch("/applications/<int:application_id>/status")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Applications"],
        "parameters": [
            {
                "name": "application_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["status"],
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["new", "reviewed", "shortlisted", "rejected"],
                            },
                            "reviewed_by": {"type": "string"},
                        },
                    }
                }
            },
        },
        "responses": {200: {"description": "Status updated"}, 400: {"description": "Invalid status"}, 404: {"description": "Not found"}},
    }
)
def update_application_status(application_id: int):
    application = db.session.get(Application, application_id)
    if application is None:
        return jsonify({"error": "application not found"}), 404

    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status not in VALID_STATUSES:
        return jsonify({"error": "invalid status value"}), 400

    application.status = status
    application.reviewed_by = payload.get("reviewed_by")
    application.reviewed_at = datetime.now(UTC)
    db.session.commit()
    return jsonify(application.to_dict()), 200


@applications_bp.post("/applications/<int:application_id>/notes")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Applications"],
        "parameters": [
            {
                "name": "application_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["author_name", "note_text"],
                        "properties": {
                            "author_name": {"type": "string"},
                            "note_text": {"type": "string"},
                        },
                    }
                }
            },
        },
        "responses": {201: {"description": "Note created"}, 400: {"description": "Invalid payload"}, 404: {"description": "Not found"}},
    }
)
def create_application_note(application_id: int):
    application = db.session.get(Application, application_id)
    if application is None:
        return jsonify({"error": "application not found"}), 404

    payload = request.get_json(silent=True) or {}
    author_name = payload.get("author_name")
    note_text = payload.get("note_text")

    if not author_name or not note_text:
        return jsonify({"error": "author_name and note_text are required"}), 400

    note = ReviewNote(
        application_id=application_id,
        author_name=author_name.strip(),
        note_text=note_text.strip(),
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201


@applications_bp.get("/applications/<int:application_id>/notes")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Applications"],
        "parameters": [
            {
                "name": "application_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        "responses": {200: {"description": "List notes"}, 404: {"description": "Not found"}},
    }
)
def list_application_notes(application_id: int):
    application = db.session.get(Application, application_id)
    if application is None:
        return jsonify({"error": "application not found"}), 404

    notes = (
        ReviewNote.query.filter_by(application_id=application_id)
        .order_by(ReviewNote.created_at.asc())
        .all()
    )
    return jsonify([note.to_dict() for note in notes]), 200


@applications_bp.post("/applications/score")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Applications"],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["application_id"],
                        "properties": {
                            "application_id": {"type": "integer"},
                            "weights": {
                                "type": "object",
                                "properties": {
                                    "skills": {"type": "number"},
                                    "experience": {"type": "number"},
                                    "education": {"type": "number"},
                                    "keywords": {"type": "number"},
                                },
                            },
                        },
                    }
                }
            },
        },
        "responses": {
            200: {"description": "Score computed"},
            400: {"description": "Invalid payload"},
            404: {"description": "Application not found"},
        },
    }
)
def score_application():
    payload = request.get_json(silent=True) or {}
    application_id = payload.get("application_id")
    if application_id is None:
        return jsonify({"error": "application_id is required"}), 400

    application = db.session.get(Application, application_id)
    if application is None:
        return jsonify({"error": "application not found"}), 404

    candidate = db.session.get(Candidate, application.candidate_id)
    jd = db.session.get(JobDescription, application.jd_id)
    if candidate is None or jd is None:
        return jsonify({"error": "candidate or job description not found"}), 400

    result = score_candidate_against_jd(
        candidate=candidate.to_dict(),
        jd=jd.to_dict(),
        weights=payload.get("weights"),
    )

    application.total_score = result.total_score
    application.score_breakdown_json = result.breakdown
    db.session.commit()

    return (
        jsonify(
            {
                "application_id": application.id,
                "total_score": application.total_score,
                "score_breakdown_json": application.score_breakdown_json,
            }
        ),
        200,
    )
