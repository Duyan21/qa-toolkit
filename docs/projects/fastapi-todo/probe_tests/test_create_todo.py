import requests
import pytest

from conftest import BASE_URL


# --- Probe 1: Full valid payload ---
def test_create_todo_full_payload():
    payload = {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "status": "pending"
    }

    response = requests.post(f"{BASE_URL}/todos/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["status"] == "pending"
    assert isinstance(data["id"], int)
    assert data["id"] > 0


# --- Probe 2: Title only — description and status should use defaults ---
def test_create_todo_title_only():
    payload = {"title": "Minimal todo"}

    response = requests.post(f"{BASE_URL}/todos/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Minimal todo"
    assert data["description"] is None   # GAP if API differs
    assert data["status"] == "pending"   # GAP if API differs


# --- Probe 3: Missing title field entirely ---
def test_create_todo_missing_title():
    payload = {
        "description": "No title here",
        "status": "pending"
    }

    response = requests.post(f"{BASE_URL}/todos/", json=payload)

    assert response.status_code == 422


# --- Probe 4: title explicitly set to null ---
def test_create_todo_null_title():
    payload = {"title": None}

    response = requests.post(f"{BASE_URL}/todos/", json=payload)

    assert response.status_code == 422


# --- Probe 5: Empty body ---
def test_create_todo_empty_body():
    response = requests.post(f"{BASE_URL}/todos/", json={})

    assert response.status_code == 422


# --- Probe 6: Empty string title — GAP: no min-length validation expected ---
def test_create_todo_empty_string_title():
    payload = {"title": ""}

    response = requests.post(f"{BASE_URL}/todos/", json=payload)

    # GAP: FastAPI does not enforce min_length by default — likely accepted as 200
    assert response.status_code == 200


# --- Probe 7: Very long title (10k chars) — GAP: no max-length validation expected ---
def test_create_todo_very_long_title():
    payload = {"title": "A" * 10_000}

    response = requests.post(f"{BASE_URL}/todos/", json=payload)

    # GAP: no max_length constraint defined — likely accepted as 200
    assert response.status_code == 200
    data = response.json()
    assert len(data["title"]) == 10_000


# --- Probe 8: Unknown extra fields — should be ignored ---
def test_create_todo_extra_fields_ignored():
    payload = {
        "title": "Todo with extras",
        "unknown_field": "should be ignored",
        "another_extra": 42
    }

    response = requests.post(f"{BASE_URL}/todos/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "unknown_field" not in data
    assert "another_extra" not in data


# --- Probe 9: SQL injection in title — SQLAlchemy should store it literally ---
def test_create_todo_sql_injection_in_title():
    malicious_title = "'; DROP TABLE todos; --"
    payload = {"title": malicious_title}

    response = requests.post(f"{BASE_URL}/todos/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == malicious_title  # stored as-is, not executed


# --- Probe 10: Create then GET /{id} — confirms data persists correctly ---
def test_create_todo_then_get_by_id():
    payload = {
        "title": "Persistence check",
        "description": "Should survive a GET",
        "status": "pending"
    }

    create_response = requests.post(f"{BASE_URL}/todos/", json=payload)
    assert create_response.status_code == 200
    created = create_response.json()
    todo_id = created["id"]

    get_response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()

    assert fetched["id"] == todo_id
    assert fetched["title"] == payload["title"]
    assert fetched["description"] == payload["description"]
    assert fetched["status"] == payload["status"]
