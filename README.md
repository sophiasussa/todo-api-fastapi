# Todo API – FastAPI

[![CI](https://github.com/sophiasussa/todo-api-fastapi/actions/workflows/ci.yml/badge.svg)](https://github.com/sophiasussa/todo-api-fastapi/actions)
[![codecov](https://codecov.io/gh/sophiasussa/todo-api-fastapi/branch/main/graph/badge.svg)](https://codecov.io/gh/sophiasussa/todo-api-fastapi)

REST API for task management built with FastAPI, focusing on backend engineering practices, automated testing, and continuous integration.

Live API Docs (Swagger)
https://todo-api-latest-82ru.onrender.com/docs

---

## Technologies

* Python 3.11
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pytest
* Docker
* GitHub Actions (CI)
* Codecov
* Alembic (database migrations)

---

## Project Structure

```
app/
 ├── exceptions/
 ├── models/
 ├── routes/
 ├── database/
 ├── schemas/
 ├── services/
 └── main.py

tests/
 ├── unit/
 └── integration/
```

---

## Testing

The project includes two types of automated tests:

* **Unit Tests**: fast, isolated and use SQLite in-memory
* **Integration Tests**: use a real PostgreSQL database and run in an isolated Docker environment

### Run in an isolated Docker environment

```bash
pytest -m unit
pytest -m integration
```

### Run tests with coverage

```bash
pytest --cov=app
```

---

## Code Coverage

Test coverage is automatically monitored using **Codecov**.

* Minimum required coverage: **70%**
* Pull Requests fail if coverage drops below the threshold.

---

## CI – Continuous Integration

A CI pipeline runs automatically using GitHub Actions on:

* Push to `main` or `develop`
* Pull Requests

Pipeline steps:

1. Install dependencies
2. Run unit tests
3. Run integration tests
4. Generate coverage report
5. Upload coverage to Codecov

---

## Running the API Locally

The API and PostgreSQL database run in containers using Docker Compose.

Start the environment:
```bash
docker compose up -d
```

The interactive API documentation will be available at:

http://localhost:8000/docs

---

Deployment

The application is deployed using Docker containers on Render.

During container startup:
 - Database migrations run automatically via Alembic
 - The FastAPI application is started with Uvicorn
   
---

## License

This project was developed for learning and portfolio purposes.
