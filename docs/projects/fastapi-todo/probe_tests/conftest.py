import pytest
import requests

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(autouse=True)
def cleanup_after_test():
    yield
    response = requests.get(f"{BASE_URL}/todos/", params={"limit": 1000})
    if response.status_code != 200:
        return
    for todo in response.json():
        requests.delete(f"{BASE_URL}/todos/{todo['id']}")


@pytest.fixture
def existing_todo():
    """Pre-creates a todo for tests that need an existing record (GET, PUT, DELETE)."""
    payload = {"title": "Fixture todo", "description": "Created by fixture", "status": "pending"}
    response = requests.post(f"{BASE_URL}/todos/", json=payload)
    return response.json()
