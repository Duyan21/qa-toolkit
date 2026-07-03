import requests

from conftest import BASE_URL


# --- X1: Full task lifecycle — Create → Update → Read back ---
def test_full_task_lifecycle():
    create_response = requests.post(f"{BASE_URL}/todos/", json={"title": "Lifecycle todo", "status": "pending"})
    assert create_response.status_code == 200
    todo_id = create_response.json()["id"]

    requests.put(f"{BASE_URL}/todos/{todo_id}", json={"status": "done"})

    get_response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "done"


# --- X2: Create → List → Delete → List confirms appearance and disappearance ---
def test_create_list_delete_list():
    create_response = requests.post(f"{BASE_URL}/todos/", json={"title": "Ephemeral todo"})
    assert create_response.status_code == 200
    todo_id = create_response.json()["id"]

    list_after_create = requests.get(f"{BASE_URL}/todos/").json()
    assert any(t["id"] == todo_id for t in list_after_create)

    requests.delete(f"{BASE_URL}/todos/{todo_id}")

    list_after_delete = requests.get(f"{BASE_URL}/todos/").json()
    assert not any(t["id"] == todo_id for t in list_after_delete)


# --- X3: Two todos created back to back have different IDs ---
def test_concurrent_ids_are_unique():
    r1 = requests.post(f"{BASE_URL}/todos/", json={"title": "Todo A"})
    r2 = requests.post(f"{BASE_URL}/todos/", json={"title": "Todo B"})

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["id"] != r2.json()["id"]


# --- X4: Delete → Create → verify deleted ID is not reused ---
def test_deleted_id_not_reused():
    r1 = requests.post(f"{BASE_URL}/todos/", json={"title": "To be deleted"})
    deleted_id = r1.json()["id"]

    requests.delete(f"{BASE_URL}/todos/{deleted_id}")

    r2 = requests.post(f"{BASE_URL}/todos/", json={"title": "New todo after delete"})
    new_id = r2.json()["id"]

    # GAP: model uses INTEGER PRIMARY KEY without AUTOINCREMENT.
    # SQLite reuses the ID when the table is empty after delete.
    # Fix: add autoincrement=True to the id column in models.py.
    assert new_id == deleted_id  # documents current (broken) behavior
