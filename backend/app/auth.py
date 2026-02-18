from functools import wraps

from flask import g, jsonify, request

from app.extensions import db
from app.models.user import User
from app.services.auth import verify_access_token


def require_auth(roles: set[str] | None = None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            prefix = "Bearer "
            if not auth_header.startswith(prefix):
                return jsonify({"error": "authorization token is required"}), 401

            token = auth_header[len(prefix) :].strip()
            payload = verify_access_token(token)
            if payload is None:
                return jsonify({"error": "invalid or expired token"}), 401

            user = db.session.get(User, payload.get("sub"))
            if user is None or not user.is_active:
                return jsonify({"error": "user not found or inactive"}), 401

            if roles is not None and user.role not in roles:
                return jsonify({"error": "forbidden"}), 403

            g.current_user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator
