import requests

from conftest import BASE_URL


# --- D1: Delete existing todo ---
def test_delete_existing_todo(existing_todo):
    todo_id = existing_todo["id"]

    response = requests.delete(f"{BASE_URL}/todos/{todo_id}")

    assert response.status_code == 200
    assert response.json()["detail"] == "Todo deleted"


# --- D2: GET after delete returns 404 — confirms hard delete ---
def test_get_after_delete(existing_todo):
    todo_id = existing_todo["id"]
    requests.delete(f"{BASE_URL}/todos/{todo_id}")

    response = requests.get(f"{BASE_URL}/todos/{todo_id}")

    assert response.status_code == 404


# --- D3: Deleted item absent from list ---
def test_deleted_item_absent_from_list(existing_todo):
    todo_id = existing_todo["id"]
    requests.delete(f"{BASE_URL}/todos/{todo_id}")

    response = requests.get(f"{BASE_URL}/todos/")

    ids = [t["id"] for t in response.json()]
    assert todo_id not in ids


# --- D4: Delete non-existent ID ---
def test_delete_nonexistent_todo():
    response = requests.delete(f"{BASE_URL}/todos/9999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


# --- D5: Double delete — first 200, second 404 (not idempotent) ---
def test_double_delete(existing_todo):
    todo_id = existing_todo["id"]

    first = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    second = requests.delete(f"{BASE_URL}/todos/{todo_id}")

    assert first.status_code == 200
    assert second.status_code == 404
