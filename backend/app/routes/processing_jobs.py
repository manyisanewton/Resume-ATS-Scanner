from flask import Blueprint, jsonify
from flasgger import swag_from

from app.auth import require_auth
from app.extensions import db
from app.models.processing_job import ProcessingJob

processing_jobs_bp = Blueprint("processing_jobs", __name__)


@processing_jobs_bp.get("/processing-jobs/<int:job_id>")
@require_auth(roles={"admin", "recruiter"})
@swag_from(
    {
        "tags": ["Processing Jobs"],
        "parameters": [
            {
                "name": "job_id",
                "in": "path",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        "responses": {200: {"description": "Job detail"}, 404: {"description": "Not found"}},
    }
)
def get_processing_job(job_id: int):
    job = db.session.get(ProcessingJob, job_id)
    if job is None:
        return jsonify({"error": "processing job not found"}), 404
    return jsonify(job.to_dict()), 200
