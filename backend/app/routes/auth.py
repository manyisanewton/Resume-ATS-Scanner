from flask import Blueprint, g, jsonify, request
from flasgger import swag_from

from app.auth import require_auth
from app.extensions import db
from app.models.user import User
from app.services.auth import generate_access_token

auth_bp = Blueprint("auth", __name__)
users_bp = Blueprint("users", __name__)


@auth_bp.post("/auth/bootstrap-admin")
@swag_from(
    {
        "tags": ["Auth"],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["username", "password"],
                        "properties": {
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                        },
                    }
                }
            },
        },
        "responses": {201: {"description": "Admin created"}, 400: {"description": "Already initialized or invalid"}},
    }
)
def bootstrap_admin():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    existing_admin = User.query.filter_by(role="admin").first()
    if existing_admin is not None:
        return jsonify({"error": "admin already exists"}), 400

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "username already exists"}), 400

    user = User(username=username, role="admin", is_active=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "admin created", "user": user.to_dict()}), 201


@auth_bp.post("/auth/login")
@swag_from(
    {
        "tags": ["Auth"],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["username", "password"],
                        "properties": {
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                        },
                    }
                }
            },
        },
        "responses": {200: {"description": "Authenticated"}, 401: {"description": "Invalid credentials"}},
    }
)
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if user is None or not user.is_active or not user.check_password(password):
        return jsonify({"error": "invalid username or password"}), 401

    token = generate_access_token(user_id=user.id, role=user.role)
    return jsonify({"access_token": token, "user": user.to_dict()}), 200


@users_bp.get("/users/me")
@require_auth(roles={"admin", "recruiter"})
@swag_from({"tags": ["Users"], "responses": {200: {"description": "Current user"}}})
def me():
    return jsonify(g.current_user.to_dict()), 200


@users_bp.post("/users/recruiters")
@require_auth(roles={"admin"})
@swag_from(
    {
        "tags": ["Users"],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["username", "password"],
                        "properties": {
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                        },
                    }
                }
            },
        },
        "responses": {201: {"description": "Recruiter created"}, 400: {"description": "Invalid payload"}, 403: {"description": "Forbidden"}},
    }
)
def create_recruiter():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "username already exists"}), 400

    recruiter = User(username=username, role="recruiter", is_active=True)
    recruiter.set_password(password)
    db.session.add(recruiter)
    db.session.commit()

    return jsonify({"message": "recruiter created", "user": recruiter.to_dict()}), 201
