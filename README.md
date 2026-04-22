# ParkIT Backend

Flask REST API for the ParkIT parking service application.

## Prerequisites

- Python 3.13+
- PostgreSQL (or Docker + Docker Compose)

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the `Backend/` root directory:

```ini
FLASK_ENV=development
DATABASE_URL=postgresql://<user>:<password>@127.0.0.1:5432/parkit
```

### 3. Start the database

Using Docker Compose (recommended):

```bash
docker-compose up db -d
```

This starts a PostgreSQL 17 container on port `5432` with:
- User: `parkit`
- Password: `superdupersecret12345`
- Database: `parkit`

So the `DATABASE_URL` for Docker would be:

```
DATABASE_URL=postgresql://parkit:superdupersecret12345@127.0.0.1:5432/parkit
```

## Running the App

```bash
flask --app wsgi.py run
```

Or with Docker Compose (starts both db and web):

```bash
docker-compose up
```

## Running Tests

Tests live in `tests/` and are split into `unit/` and `integration/`. Integration tests require a running PostgreSQL database.

### Run all tests

```bash
pytest
```

### Run only unit tests

```bash
pytest tests/unit/
```

### Run only integration tests

```bash
pytest tests/integration/
```

### Run a specific test file

```bash
pytest tests/integration/api/auth/test_auth_login.py
```

### Run with verbose output

```bash
pytest -v
```

### Run with coverage

```bash
coverage run -m pytest
coverage report
```

For an HTML coverage report:

```bash
coverage html
open htmlcov/index.html
```

## Test Structure

```
tests/
├── conftest.py              # Fixtures: app, client, session, runner, auth
├── util.py                  # Shared test helpers
├── unit/
│   ├── model/               # Unit tests for models and repositories
│   ├── test_config.py
│   ├── test_database.py
│   └── test_exceptions.py
└── integration/
    ├── api/
    │   ├── auth/            # Login, register, token, refresh
    │   └── account/         # Account CRUD endpoints
    ├── test_base.py
    ├── test_commands.py
    ├── test_db.py
    └── test_factory.py
```

## Linting

Configuration for both tools is in `setup.cfg` (max line length: 120, migrations and venv excluded).

### Check for style violations

```bash
flake8 app/
```

### Check import ordering

```bash
isort --check-only --diff app/
```

### Auto-fix import ordering

```bash
isort app/
```