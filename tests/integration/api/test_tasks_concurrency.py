from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
import pytest
from app.main import app

pytestmark = pytest.mark.concurrency

def make_client():
    return TestClient(app)

def complete_task_request(task_id: int):
    client = make_client()
    return client.patch(f"/tasks/{task_id}/complete")

def delete_task_request(task_id: int):
    client = make_client()
    return client.delete(f"/tasks/{task_id}")

def update_task_request(task_id: int, title: str):
    client = make_client()
    return client.put(
        f"/tasks/{task_id}",
        json={"title": title}
    )

def create_and_complete_task(title: str):
    client = make_client()

    task = client.post("/tasks/", json={"title": title}).json()
    client.patch(f"/tasks/{task['id']}/complete")

    return task["id"]

def test_complete_task_concurrently(client):
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
    assert status_codes == [204, 404]

def test_update_task_concurrently(client):
    task = client.post("/tasks/", json={"title": "Inicial"}).json()
    task_id = task["id"]

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(
                lambda title: update_task_request(task_id, title),
                ["A", "B"],
            )
        )

    assert all(r.status_code == 200 for r in responses)

    final = client.get(f"/tasks/{task_id}").json()
    assert final["title"] in ["A", "B"]


def test_update_task_not_found(client):
    response = client.put("/tasks/123", json={"title": "Novo título"})

    assert response.status_code == 404
    assert response.json()["error_code"] == "TASK_NOT_FOUND"


def test_each_request_uses_isolated_db_session_under_concurrency(client):
    with ThreadPoolExecutor(max_workers=2) as executor:
        ids = list(
            executor.map(
                create_and_complete_task,
                ["Task A", "Task B"],
            )
        )

    # verifica que ambas existem e estão completas
    for task_id in ids:
        response = client.get(f"/tasks/{task_id}")
        data = response.json()

        assert response.status_code == 200
        assert data["done"] is True
