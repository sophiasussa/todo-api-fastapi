"""
Integration tests for Task API endpoints.

This module validates the full HTTP lifecycle:

Request → FastAPI router → Service layer → Database → Response

Characteristics:
- Marked as integration tests
- Uses real database (TEST_DATABASE_URL)
- Uses FastAPI TestClient
- Validates HTTP status codes, response payloads and error contracts

These tests ensure:
- API contract correctness
- Business rule enforcement
- Proper error handling (including Problem Details format)
"""

import pytest

# ID guaranteed not to exist in tests
NON_EXISTENT_ID = 999

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


def test_create_task(client):
    """
    Test successful task creation.

    Validates:
    - HTTP 201 status code
    - Correct response structure
    - Default `done` value is False
    - ID is generated
    """
    response = client.post("/tasks/", json={"title": "Estudar FastAPI"})

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Estudar FastAPI"
    assert data["done"] is False
    assert "id" in data


@pytest.mark.parametrize(
    "title",
    ["", "a", "ab", " " * 5, "a" * 200],
)
def test_create_task_invalid_titles(client, title):
    """
    Test validation errors when creating tasks with invalid titles.

    Ensures:
    - Invalid input returns HTTP 422
    - Request is rejected before reaching business logic
    """
    response = client.post("/tasks/", json={"title": title})
    assert response.status_code == 422


def test_complete_task_already_completed(client):
    """
    Test completing a task that is already completed.

    Ensures:
    - Second completion attempt returns 400
    - Proper domain-specific error code is returned
    """
    task = client.post("/tasks/", json={"title": "Teste"}).json()

    client.patch(f"/tasks/{task['id']}/complete")
    response = client.patch(f"/tasks/{task['id']}/complete")

    assert response.status_code == 400
    assert response.json()["error_code"] == "TASK_ALREADY_COMPLETED"


def test_get_task_not_found(client):
    """
    Test retrieving a task that does not exist.

    Ensures:
    - HTTP 404 is returned
    - Proper domain error code is included
    """
    response = client.get(f"/tasks/{NON_EXISTENT_ID}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "TASK_NOT_FOUND"


def test_delete_task_not_found(client):
    """
    Test deleting a non-existent task.

    Ensures:
    - HTTP 404 is returned
    - Proper error code is included
    """
    response = client.delete(f"/tasks/{NON_EXISTENT_ID}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "TASK_NOT_FOUND"


def test_list_tasks_filters_only_completed_when_done_true(client):
    """
    Test filtering tasks by `done=true`.

    Ensures:
    - Only completed tasks are returned
    - Filtering logic works correctly at API level
    """
    t1 = client.post("/tasks/", json={"title": "Task A"}).json()
    client.post("/tasks/", json={"title": "Task B"})

    client.patch(f"/tasks/{t1['id']}/complete")

    response = client.get("/tasks/?done=true")
    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == t1["id"]
    assert data[0]["done"] is True


@pytest.mark.parametrize(
    "done_value,expected_count",
    [
        (True, 1),
        (False, 1),
    ]
)
def test_list_tasks_filtered(client, done_value, expected_count):
    """
    Test filtering tasks using the `done` query parameter.

    Ensures:
    - HTTP 200 response
    - Correct number of filtered results
    """
    t1 = client.post("/tasks/", json={"title": "Task A"}).json()
    client.post("/tasks/", json={"title": "Task B"})

    client.patch(f"/tasks/{t1['id']}/complete")

    response = client.get(f"/tasks/?done={str(done_value).lower()}")
    assert response.status_code == 200
    assert len(response.json()) == expected_count


def test_problem_details_format(client):
    """
    Test RFC-style Problem Details error format.

    Ensures:
    - Response follows standardized error structure
    - Contains required fields:
        - type
        - title
        - detail
        - status
        - instance
        - error_code
    """
    task = client.post("/tasks/", json={"title": "RFC"}).json()

    client.patch(f"/tasks/{task['id']}/complete")
    response = client.patch(f"/tasks/{task['id']}/complete")

    data = response.json()

    assert response.status_code == 400
    assert data["type"].startswith("https://")
    assert data["title"]
    assert data["detail"]
    assert data["status"] == 400
    assert data["instance"] == f"/tasks/{task['id']}/complete"
    assert data["error_code"] == "TASK_ALREADY_COMPLETED"


@pytest.mark.parametrize(
    "method,url",
    [
        ("get", f"/tasks/{NON_EXISTENT_ID}"),
        ("delete", f"/tasks/{NON_EXISTENT_ID}"),
        ("put", f"/tasks/{NON_EXISTENT_ID}"),
        ("patch", f"/tasks/{NON_EXISTENT_ID}/complete"),
    ]
)
def test_task_not_found_across_endpoints(client, method, url):
    """
    Ensure consistent 404 behavior across all task endpoints.

    Validates:
    - All endpoints return 404 for non-existent task IDs
    - Error code is standardized as TASK_NOT_FOUND
    """
    response = getattr(client, method)(url)
    assert response.status_code == 404
    assert response.json()["error_code"] == "TASK_NOT_FOUND"
