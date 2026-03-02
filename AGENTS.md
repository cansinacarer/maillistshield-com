# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Mail List Shield is a Flask-based email validation SaaS (Service 1 of 6 in a microservices architecture). This repo contains only the web UI, auth, billing, and API gateway service. The other 5 microservices (file intake, queue publisher, validation orchestrator, email validation worker, results file generator) live in separate repositories.

### Python version

The project requires **Python 3.11** (matching the devcontainer). A virtualenv is located at `/workspace/.venv`. Always activate it before running commands:

```bash
source /workspace/.venv/bin/activate
```

### Environment variables

All config is loaded at import time via `python-decouple`. The app will crash with `UndefinedValueError` if any env var is missing. A `.env` file with placeholder values is present at the repo root. For local dev without real external services, the placeholder values are sufficient to start the app and run tests.

Key defaults: SQLite is used as the database fallback (`DATABASE_CONNECTION_STRING` defaults to `sqlite:///database.db`), and Google reCAPTCHA test keys are configured so captcha auto-passes locally.

### Running the app

```bash
FLASK_APP=run.py flask run --debug --cert=.devcontainer/ssl/cert.pem --key=.devcontainer/ssl/key.pem --port 5000
```

The app runs on **https://localhost:5000** (HTTPS with self-signed certs). When testing in a browser, you must bypass the SSL certificate warning.

### Running tests

```bash
pytest -v
```

Tests use SQLite (the `test_config=True` flag disables Postgres connection pooling). No external services are needed to run the test suite.

### Linting

```bash
black --check app/ tests/ run.py
```

### Important gotchas

- The `config.py` module-level code initializes an S3 boto3 resource at import time. Even though it uses placeholder credentials, this means the `S3_ENDPOINT`, `S3_KEY`, and `S3_SECRET` env vars must be set before importing anything from the app.
- Registration and login flows require email verification (6-digit code). Since SMTP uses placeholder credentials locally, emails won't actually send. For testing auth flows beyond registration, you may need to directly modify the database to set `email_confirmed=1` on the test user.
- The `.devcontainer/ssl/` directory contains self-signed certificates required when `FLASK_DEBUG=True`. The `FLASK_RUN_CERT` and `FLASK_RUN_KEY` env vars must point to these files.
