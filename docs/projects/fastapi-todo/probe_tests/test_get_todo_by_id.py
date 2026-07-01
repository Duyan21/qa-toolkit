import requests

from conftest import BASE_URL


# --- G1: Get existing todo by valid ID ---
def test_get_existing_todo(existing_todo):
    todo_id = existing_todo["id"]

    response = requests.get(f"{BASE_URL}/todos/{todo_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == existing_todo["title"]
    assert data["description"] == existing_todo["description"]
    assert data["status"] == existing_todo["status"]


# --- G2: Non-existent ID ---
def test_get_nonexistent_todo():
    response = requests.get(f"{BASE_URL}/todos/9999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


# --- G3: String ID — FastAPI path type validation ---
def test_get_todo_string_id():
    response = requests.get(f"{BASE_URL}/todos/abc")

    assert response.status_code == 422


# --- G4: Negative ID — no such record, should not crash ---
def test_get_todo_negative_id():
    response = requests.get(f"{BASE_URL}/todos/-1")

    assert response.status_code == 404


# --- G5: Zero ID — auto-increment starts at 1 ---
def test_get_todo_zero_id():
    response = requests.get(f"{BASE_URL}/todos/0")

    assert response.status_code == 404
