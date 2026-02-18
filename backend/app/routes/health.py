from flask import Blueprint, jsonify
from flasgger import swag_from

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
@swag_from({
    "tags": ["Health"],
    "responses": {
        200: {
            "description": "Service health status",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/HealthResponse"}
                }
            },
        }
    },
})
def health_check():
    return jsonify({"status": "ok"}), 200
