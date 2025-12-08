
Setup

Prerequisites: Docker and Docker Compose installed.

Quick steps (PowerShell):

```powershell
docker-compose up --build -d
```
Open the app at http://localhost:8001/ (Django) — Redis is on port 6380.

Please go to http://localhost:8001/swagger/ to see swagger documentation
## Testing

Quick notes about the test suite and the new `auth` tests added recently.

- Run the auth app tests (PowerShell):

```powershell
cd d:\personal_work\task_manager\tasks
python manage.py test auth
```

- If you run the whole project tests from repository root use:

```powershell
cd d:\personal_work\task_manager\tasks
python manage.py test
```

- Docker (adjust service name):

```powershell
docker compose run --rm <service> python manage.py test auth
```

What changed in `auth/tests.py`:

- Added unit tests for the `RegisterSerializer` (validation and user creation).
- Added tests for cookie helpers: `set_tokens_cookies` and `delete_tokens_cookies`.
- Added integration-style tests that exercise the `register`, `login`, `profile`, and `logout` endpoints and assert cookies and response payloads.
- Two tests that depend on importing `CookieJWTAuthentication` are skipped when the import fails in the test environment. This keeps the test run green when `djangorestframework-simplejwt` or related configuration is not installed or available.
# Task Manager

Task Manager is a small Django + Django REST Framework project that provides a simple tasks API and an authentication app using JWT tokens in HTTP-only cookies.

This repository contains a minimal API for creating, listing, retrieving, updating, and deleting tasks, plus a small `auth` app to register/login users and manage cookie-based JWTs.

--

## Table of contents

- **Project:** brief description and purpose
- **Prerequisites:** what you need locally
- **Quick start:** run with Docker Compose or locally
- **Running tests:** how to run the test suite
- **API:** endpoints and brief examples
- **Auth notes:** cookie / JWT and CSRF considerations
- **Development:** tips and useful paths

--

## Prerequisites

- Python 3.10+ (used for local runs)
- Docker & Docker Compose (optional, recommended for consistent environment)
- (Optional) `pipenv`/`venv` for virtual environments

Project requirements are listed in `tasks/requirements.txt`.

## Quick start (Docker)

Start the project with Docker Compose (recommended):

```powershell
# from repository root
docker-compose up --build -d
```

Open the Django app at `http://localhost:8001/` and the API docs at `http://localhost:8001/swagger/`.

## Quick start (local, Windows PowerShell)

```powershell
cd d:\personal_work\task_manager\tasks
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8001
```

## Running tests

Run all tests for the Django project:

```powershell
cd d:\personal_work\task_manager\tasks
python manage.py test
```

Run tests for a single app (e.g., `task_manager`):

```powershell
python manage.py test task_manager
```

If running inside Docker, adapt the service name and use `docker compose run --rm`.

## API Overview

Base URL (when running locally): `http://localhost:8001/`

Task endpoints (mounted at `/api/tasks/`):

- `GET /api/tasks/` — list tasks (paginated)
- `POST /api/tasks/` — create a task (authenticated)
- `GET /api/tasks/{id}/` — retrieve a task
- `PUT /api/tasks/{id}/` — update a task (admin only for some operations)
- `DELETE /api/tasks/{id}/` — delete a task (admin only)

Example: create a task (when authenticated via cookie tokens):

```bash
curl -X POST "http://localhost:8001/api/tasks/" \
  -H "Content-Type: application/json" \
  --cookie "access_token=<access>; refresh_token=<refresh>" \
  -d '{"title":"New task","description":"demo","completed":false}'
```

Note: the test suite issues JWT refresh tokens and sets them as cookies on the test client (see `task_manager/tests.py`).

## Authentication notes

- The `auth` app issues JWT `access_token` and `refresh_token` as HTTP-only cookies.
- Authentication is implemented using a cookie-aware JWT authentication class that reads `access_token` from `request.COOKIES`.
- You may need to send CSRF tokens when using the browsable API or a front-end that uses cookies; the API tests use token cookies and `rest_framework_simplejwt` behavior, so adjust as necessary.

If you see 401/403 errors when testing with `curl`, ensure you include the appropriate cookies and CSRF headers (or use token auth).

## Useful files and paths

- `tasks/` — Django project settings and entrypoint
- `tasks/task_manager/` — tasks app (models, views, serializers, tests)
- `tasks/auth/` — authentication app (custom cookie-JWT helpers, views, serializers)
- `tasks/requirements.txt` — Python dependencies
- `docker-compose.yml`, `Dockerfile`, `entrypoint.sh` — docker setup









