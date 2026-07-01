import requests

from conftest import BASE_URL


# --- U1: Update all fields ---
def test_update_todo_all_fields(existing_todo):
    todo_id = existing_todo["id"]
    payload = {"title": "Updated title", "description": "Updated desc", "status": "done"}

    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["description"] == "Updated desc"
    assert data["status"] == "done"


# --- U2: Update one field only — others must remain unchanged ---
def test_update_todo_partial_update(existing_todo):
    todo_id = existing_todo["id"]

    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json={"status": "done"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["title"] == existing_todo["title"]
    assert data["description"] == existing_todo["description"]


# --- U3: Empty body — nothing should change (exclude_unset guards this) ---
def test_update_todo_empty_body(existing_todo):
    todo_id = existing_todo["id"]

    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == existing_todo["title"]
    assert data["description"] == existing_todo["description"]
    assert data["status"] == existing_todo["status"]


# --- U4: Update non-existent ID ---
def test_update_todo_nonexistent_id():
    response = requests.put(f"{BASE_URL}/todos/9999999", json={"title": "Ghost"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


# --- U5: Explicit null title — GAP: crashes endpoint with 500 ---
def test_update_todo_explicit_null_title(existing_todo):
    todo_id = existing_todo["id"]

    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json={"title": None})

    # GAP: TodoUpdate accepts null (Optional[str]), writes NULL to DB,
    # then FastAPI crashes serializing TodoOut.title: str → 500.
    # Root fix: add `title: str` (non-optional) to TodoUpdate, or
    # add a validator rejecting null on update.
    assert response.status_code == 500


# --- U6: Arbitrary status value — GAP: no enum enforcement ---
def test_update_todo_arbitrary_status(existing_todo):
    todo_id = existing_todo["id"]

    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json={"status": "in_progress"})

    # GAP: any string accepted as status — no enum constraint
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


# --- U7: Update then read back — confirms persistence ---
def test_update_todo_then_get(existing_todo):
    todo_id = existing_todo["id"]
    payload = {"title": "Persisted update", "status": "done"}

    requests.put(f"{BASE_URL}/todos/{todo_id}", json=payload)
    get_response = requests.get(f"{BASE_URL}/todos/{todo_id}")

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["title"] == "Persisted update"
    assert data["status"] == "done"
