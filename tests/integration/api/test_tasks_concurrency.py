"""
Concurrency tests for Task API.

This module validates system behavior under concurrent requests.

These tests simulate multiple clients interacting with the same
resource simultaneously using ThreadPoolExecutor.

Characteristics:
- Marked as concurrency tests
- Use real database (Postgres via TEST_DATABASE_URL)
- Apply real Alembic migrations
- Each concurrent request uses a separate TestClient instance
- Validate transactional integrity and race-condition handling

These tests ensure:
- Business rules remain consistent under concurrency
- No unexpected 500 errors occur
- Database sessions are properly isolated
"""

from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
import pytest
from app.main import app


# Mark all tests in this module as concurrency tests
pytestmark = pytest.mark.concurrency


# ======================================================
# Helpers
# ======================================================

def make_client():
    """
    Create a new FastAPI TestClient instance.

    Important:
    Each concurrent request must use a separate client instance
    to ensure independent request lifecycle and DB session handling.
    """
    return TestClient(app)


def complete_task_request(task_id: int):
    """
    Send a PATCH request to complete a task.
    """
    client = make_client()
    return client.patch(f"/tasks/{task_id}/complete")


def delete_task_request(task_id: int):
    """
    Send a DELETE request for a task.
    """
    client = make_client()
    return client.delete(f"/tasks/{task_id}")


def update_task_request(task_id: int, title: str):
    """
    Send a PUT request to update a task title.
    """
    client = make_client()
    return client.put(
        f"/tasks/{task_id}",
        json={"title": title}
    )


def create_and_complete_task(title: str):
    """
    Helper used to validate session isolation.

    Creates a task and completes it within the same request flow.
    Returns the task ID.
    """
    client = make_client()

    task = client.post("/tasks/", json={"title": title}).json()
    client.patch(f"/tasks/{task['id']}/complete")

    return task["id"]


# ======================================================
# Concurrency scenarios
# ======================================================

def test_complete_task_concurrently(client):
    """
    Test concurrent completion of the same task.

    Expected behavior:
    - One request succeeds (200)
    - One request fails with business rule error (400)

    Ensures:
    - No double-completion occurs
    - Domain rule is enforced under race condition
    """
    task = client.post("/tasks/", json={"title": "Concorrente"}).json()
    task_id = task["id"]

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(
                lambda _: complete_task_request(task_id),
                range(2),
            )
        )

    status_codes = sorted(r.status_code for r in responses)
    assert status_codes == [200, 400]


def test_delete_task_concurrently(client):
    """
    Test concurrent deletion of the same task.

    Expected behavior:
    - Both requests return 204 (idempotent delete)

    This ensures:
    - No server errors occur
    - DELETE operation remains safe under concurrency
    """
    task = client.post("/tasks/", json={"title": "Delete concorrente"}).json()
    task_id = task["id"]

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(
                lambda _: delete_task_request(task_id),
                range(2),
            )
        )

    status_codes = sorted(r.status_code for r in responses)
    assert status_codes == [204, 204]


def test_update_task_concurrently(client):
    """
    Test concurrent updates to the same task.

    Expected behavior:
    - Both succeed (last write wins), OR
    - One succeeds and one returns 409 (conflict)

    Ensures:
    - No 500 errors occur
    - Database remains consistent
    - Final state matches one of the submitted values
    """
    task = client.post("/tasks/", json={"title": "Inicial"}).json()
    task_id = task["id"]

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(
                lambda title: update_task_request(task_id, title),
                ["Titulo A", "Titulo B"],
            )
        )

    assert all(r.status_code in (200, 409) for r in responses)

    final = client.get(f"/tasks/{task_id}").json()
    assert final["title"] in ["Titulo A", "Titulo B"]


def test_update_task_not_found(client):
    """
    Ensure updating a non-existent task returns 404.
    """
    response = client.put("/tasks/123", json={"title": "Novo título"})

    assert response.status_code == 404
    assert response.json()["error_code"] == "TASK_NOT_FOUND"


def test_each_request_uses_isolated_db_session_under_concurrency(client):
    """
    Validate database session isolation under concurrent execution.

    Scenario:
    - Two tasks are created and completed in parallel
    - Each operation must use an independent DB session
    - No cross-session interference should occur

    Ensures:
    - Proper session handling
    - Thread-safe dependency override behavior
    """
    with ThreadPoolExecutor(max_workers=2) as executor:
        ids = list(
            executor.map(
                create_and_complete_task,
                ["Task A", "Task B"],
            )
        )

    # Verify both tasks exist and are completed
    for task_id in ids:
        response = client.get(f"/tasks/{task_id}")
        data = response.json()

        assert response.status_code == 200
        assert data["done"] is True
