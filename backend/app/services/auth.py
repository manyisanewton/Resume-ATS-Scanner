from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer

from flask import current_app


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="auth-token")


def generate_access_token(user_id: int, role: str) -> str:
    payload = {"sub": user_id, "role": role}
    return _serializer().dumps(payload)


def verify_access_token(token: str) -> dict | None:
    max_age = current_app.config.get("TOKEN_MAX_AGE_SECONDS", 60 * 60 * 8)
    try:
        data = _serializer().loads(token, max_age=max_age)
    except (BadSignature, BadTimeSignature):
        return None

    if not isinstance(data, dict):
        return None
    if "sub" not in data or "role" not in data:
        return None
    return data
