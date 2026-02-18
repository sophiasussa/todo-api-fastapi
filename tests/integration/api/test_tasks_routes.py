import pytest
NON_EXISTENT_ID = 999

def test_create_task(client):
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
    response = client.post("/tasks/", json={"title": title})
    assert response.status_code == 422


def test_complete_task_already_completed(client):
    task = client.post("/tasks/", json={"title": "Teste"}).json()

    client.patch(f"/tasks/{task['id']}/complete")
    response = client.patch(f"/tasks/{task['id']}/complete")

    assert response.status_code == 400
    assert response.json()["error_code"] == "TASK_ALREADY_COMPLETED"


def test_get_task_not_found(client):
    response = client.get(f"/tasks/{NON_EXISTENT_ID}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "TASK_NOT_FOUND"


def test_delete_task_not_found(client):
    response = client.delete(f"/tasks/{NON_EXISTENT_ID}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "TASK_NOT_FOUND"


def test_list_tasks_filters_only_completed_when_done_true(client):
    t1 = client.post("/tasks/", json={"title": "A"}).json()
    client.post("/tasks/", json={"title": "B"})

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
    t1 = client.post("/tasks/", json={"title": "A"}).json()
    client.post("/tasks/", json={"title": "B"})

    client.patch(f"/tasks/{t1['id']}/complete")

    response = client.get(f"/tasks/?done={str(done_value).lower()}")
    assert response.status_code == 200
    assert len(response.json()) == expected_count


def test_problem_details_format(client):
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
    response = getattr(client, method)(url)
    assert response.status_code == 404
    assert response.json()["error_code"] == "TASK_NOT_FOUND"
