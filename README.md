# Task Manager API

Async FastAPI service for users, projects, and tasks. Data lives in PostgreSQL (SQLAlchemy 2 + asyncpg). Auth is JWT. Register sends a welcome email in the background.

## Stack

- FastAPI + Uvicorn
- SQLAlchemy 2 (async) + Alembic
- PostgreSQL (`asyncpg`)
- JWT (`python-jose`) and password hashing (`pwdlib`)
- Pytest + pytest-asyncio + httpx

## Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` in the project root:

```env
SECRET_KEY=

DATABASE_USERNAME=
PASSWORD=
HOST=localhost
PORT=5432
DATABASE=

EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

Apply migrations:

```bash
alembic upgrade head
```

Run the API:

```bash
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive schema.

## API

| Method | Path | Auth |
| --- | --- | --- |
| `GET` | `/health` | No |
| `POST` | `/register` | No |
| `POST` | `/login` | No |
| `POST` / `GET` | `/projects` | Bearer |
| `GET` / `PATCH` / `DELETE` | `/projects/{id}` | Bearer |
| `POST` / `GET` | `/projects/{id}/tasks` | Bearer |
| `GET` / `PATCH` / `DELETE` | `/tasks/{id}` | Bearer |

Login returns a Bearer token. Send it as `Authorization: Bearer <token>`.

Projects and tasks are scoped to the current user. List endpoints support `page`, `limit`, `sort`, and `search`. Task priority is `LOW`, `MEDIUM`, or `HIGH` (default `MEDIUM`).

## Tests

Tests use a separate PostgreSQL database (`task_manager_test` in `tests/conftest.py`) and roll back each case.

```bash
pytest
```
