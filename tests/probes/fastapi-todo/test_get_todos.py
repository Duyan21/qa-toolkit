import requests

from conftest import BASE_URL


# --- L1: Empty database returns [] not 404 ---
def test_list_todos_when_empty():
    response = requests.get(f"{BASE_URL}/todos/")

    assert response.status_code == 200
    assert response.json() == []


# --- L2: Default pagination returns 10 items when 15 exist ---
def test_list_todos_default_limit():
    for i in range(15):
        requests.post(f"{BASE_URL}/todos/", json={"title": f"Todo {i+1}"})

    response = requests.get(f"{BASE_URL}/todos/")

    assert response.status_code == 200
    assert len(response.json()) == 10


# --- L3: skip + limit returns correct slice ---
def test_list_todos_skip_and_limit():
    # Clear all existing todos first so the count is known
    existing = requests.get(f"{BASE_URL}/todos/", params={"limit": 1000}).json()
    for todo in existing:
        requests.delete(f"{BASE_URL}/todos/{todo['id']}")

    for i in range(15):
        requests.post(f"{BASE_URL}/todos/", json={"title": f"Todo {i+1}"})

    response = requests.get(f"{BASE_URL}/todos/", params={"skip": 10, "limit": 10})

    assert response.status_code == 200
    assert len(response.json()) == 5


# --- L4: limit=0 returns empty list ---
def test_list_todos_limit_zero(existing_todo):
    response = requests.get(f"{BASE_URL}/todos/", params={"limit": 0})

    assert response.status_code == 200
    assert response.json() == []


# --- L5: skip beyond total count returns empty list ---
def test_list_todos_skip_beyond_count():
    for i in range(3):
        requests.post(f"{BASE_URL}/todos/", json={"title": f"Todo {i+1}"})

    response = requests.get(f"{BASE_URL}/todos/", params={"skip": 100})

    assert response.status_code == 200
    assert response.json() == []


# --- L6: No filtering by status — all returned regardless of status ---
def test_list_todos_no_status_filter():
    requests.post(f"{BASE_URL}/todos/", json={"title": "Pending todo", "status": "pending"})
    requests.post(f"{BASE_URL}/todos/", json={"title": "Done todo", "status": "done"})

    response = requests.get(f"{BASE_URL}/todos/")

    assert response.status_code == 200
    # By design: filtering is out of scope — confirms all statuses always returned
    statuses = [t["status"] for t in response.json()]
    assert "pending" in statuses
    assert "done" in statuses


# --- L7: Results returned in insertion order ---
def test_list_todos_insertion_order():
    titles = ["First", "Second", "Third"]
    for title in titles:
        requests.post(f"{BASE_URL}/todos/", json={"title": title})

    response = requests.get(f"{BASE_URL}/todos/")

    returned_titles = [t["title"] for t in response.json()]
    assert returned_titles == titles
