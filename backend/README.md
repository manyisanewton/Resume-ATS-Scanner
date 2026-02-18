# Backend (Flask + PostgreSQL)

## Quick Start

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Swagger UI:
- http://localhost:5000/api/docs/

## Run Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

## Database Migrations

```bash
cd backend
source .venv/bin/activate
flask --app run.py db upgrade
```

## Initial Endpoints
- `POST /api/auth/bootstrap-admin`
- `POST /api/auth/login`
- `GET /api/users/me`
- `POST /api/users/recruiters` (admin only)
- `GET /api/health`
- `POST /api/jds`
- `GET /api/jds`
- `GET /api/jds/{id}`
- `POST /api/candidates/upload`
- `GET /api/candidates/{id}`
- `POST /api/candidates/{id}/process`
- `GET /api/processing-jobs/{id}`
- `POST /api/applications`
- `GET /api/jds/{id}/applications`
- `GET /api/jds/{id}/shortlist/export.csv`
- `PATCH /api/applications/{id}/status`
- `POST /api/applications/{id}/notes`
- `GET /api/applications/{id}/notes`
- `POST /api/applications/score`

## Audit Logging

- Middleware logs every request/response audit event to `AUDIT_LOG_PATH`.
- Default path: `backend/logs/audit.log`
- Each response includes `X-Request-ID` for traceability.

## Ranked List Filters

`GET /api/jds/{id}/applications` supports:
- `sort=score_desc|score_asc`
- `min_score=<number>`
- `max_score=<number>`
- `status=new|reviewed|shortlisted|rejected`
- `skills=python,flask`
- `min_experience=<integer years>`

## Auth Flow (RBAC)

1. Bootstrap first admin (one-time):
```bash
curl -X POST http://localhost:5000/api/auth/bootstrap-admin \\
  -H \"Content-Type: application/json\" \\
  -d '{\"username\":\"admin\",\"password\":\"AdminPass123\"}'
```

2. Login as admin:
```bash
curl -X POST http://localhost:5000/api/auth/login \\
  -H \"Content-Type: application/json\" \\
  -d '{\"username\":\"admin\",\"password\":\"AdminPass123\"}'
```

3. Create recruiter (admin token required):
```bash
curl -X POST http://localhost:5000/api/users/recruiters \\
  -H \"Authorization: Bearer <ADMIN_TOKEN>\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"username\":\"recruiter1\",\"password\":\"RecruiterPass123\"}'
```
