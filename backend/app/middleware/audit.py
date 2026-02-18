import json
import logging
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from flask import Flask, g, has_request_context, request


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if has_request_context():
            record.request_id = getattr(g, "request_id", None)
        else:
            record.request_id = None
        return True


def _build_audit_logger(app: Flask) -> logging.Logger:
    logger = logging.getLogger("audit")
    if logger.handlers:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()

    configured_path = app.config.get("AUDIT_LOG_PATH", "logs/audit.log")
    log_path = Path(configured_path)
    if not log_path.is_absolute():
        log_path = Path(app.root_path).parent / log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5)
    handler.setFormatter(logging.Formatter("%(message)s"))
    handler.addFilter(RequestContextFilter())

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def init_audit_middleware(app: Flask):
    audit_logger = _build_audit_logger(app)

    @app.before_request
    def _audit_before_request():
        g.request_id = uuid4().hex
        g.started_perf = perf_counter()

    @app.after_request
    def _audit_after_request(response):
        duration_ms = 0.0
        started = getattr(g, "started_perf", None)
        if started is not None:
            duration_ms = round((perf_counter() - started) * 1000.0, 2)

        user = getattr(g, "current_user", None)
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "request_id": getattr(g, "request_id", None),
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"),
            "user_id": getattr(user, "id", None),
            "role": getattr(user, "role", None),
        }
        audit_logger.info(json.dumps(payload, ensure_ascii=True))

        response.headers["X-Request-ID"] = getattr(g, "request_id", "")
        return response
