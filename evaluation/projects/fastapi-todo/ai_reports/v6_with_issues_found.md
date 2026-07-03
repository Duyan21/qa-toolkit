# Bug Report: GET /todos endpoint returns 500 on empty database or with query parameters

## Title
`GET /todos/` endpoint crashes with 500 Internal Server Error when database is empty or query parameters are supplied

## Severity
**P1** — Core feature broken. The list endpoint is one of the five essential CRUD operations (Section 2.1 of system overview). It fails in the most common scenario (fresh start with empty database) and with standard pagination parameters (`skip`, `limit`). This blocks the user journey at the second step ("check back later to see their full list of tasks").

## What Happened

Eight tests failed, all related to `GET /todos/`:
1. **test_list_todos_when_empty** — 500 response when listing with empty database
2. **test_list_todos_default_limit** — 500 responsewhen listing with default limit
3. **test_list_todos_skip_and_limit** — 500 response when `limit=1000` query param supplied
4. **test_list_todos_no_status_filter** — 500 response (likely with status param)
5. **test_list_todos_insertion_order** — 500 response when listing
6. **test_create_list_delete_list** — 500 response when calling `GET /todos/` after create
7. **test_deleted_item_absent_from_list** — Empty response body (JSON decode error) after delete, then listing
8. **test_list_todos_skip_beyond_count** — Returnedall items instead of empty list when `skip` exceeded count

The pattern is clear: **every test that calls `GET /todos/` (with or without query params) either crashes with 500 or returns malformed responses**.

## Expected vs Actual

| Scenario | Expected | Actual |
|----------|----------|--------|
| `GET /todos/` on empty DB | 200 OK, `[]` | 500 Internal Server Error |
| `GET /todos/?skip=0&limit=10` | 200 OK, list of todos | 500 Internal Server Error |
| `GET /todos/?limit=1000` | 200 OK, all todos | 500 Internal Server Error |
| After delete, `GET /todos/` | 200 OK, list without deleted item | Empty response body (JSONDecodeError) |
| `GET /todos/?skip=100` (skip beyond count) | 200 OK, `[]` | 200 OK, returns all items (pagination ignored) |

## Root Cause Analysis

**Primary cause (500 errors):** The `GET /todos/` endpoint handler in `routers/todo.py` has a bug in how it processes query parameters or returns the response.

**Evidence:**
- All 30 tests that bypass `GET /todos/` pass (create, get-by-id, update, delete all work).
- Only tests calling `GET /todos/` fail.
- The 500 errors suggest an unhandled exception during query execution or serialization.
- Response bodies are empty (not even a JSON error object), indicating the crash happens before a response can be sent.

**Likely root cause (hypothesis based on code review in Section 4.1):**

Looking at the architecture (Section 3.1), the `GET/todos/` endpoint likely has one of these issues:

1. **Missing or incorrect handler for the list endpoint** — The handler may not exist, or the route maybe misconfigured (e.g., registered at `/` instead of `/todos/`).
2. **Unhandled exception in query construction** — The `skip`/`limit` parameters may not be properly extracted or validated, causing SQLAlchemy to throw.
3. **Response serialization failure** — The list ofORM objects may fail to serialize through `TodoOut`schema if the schema isn't configured for sequences.
4. **Database session issue** — The `get_db` dependency (Section 4.1, Step 4) may not be injecting correctly for this endpoint, causing a session error.

**Why current system health doesn't rule this out:** Section 8 (Open Questions) includes Q5: "Does thisproject have a maintained upstream?" The fact that probe tests exist but are failing suggests this was discovered during this evaluation. The system healthsummary (in the provided docs) shows the app was just updated during setup (ISS-001 resolved), which may have introduced a regression in the list endpoint.

## Impact

- **User journey blocked:** Step 2 of the end-to-end journey (Section 2.1) — "They check back later to see their full list of tasks" — is completely broken.
- **Cannot verify task creation:** Even though `POST /todos` works, users cannot confirm it succeeded by listing.
- **Cannot test pagination:** The `skip`/`limit` feature (mentioned in Section 6.2) is non-functional.
- **Tutorial users blocked:** Beginners following this as a learning project cannot progress past creating their first task without seeing the full API broken.

## Recommendation

### Immediate Action

**1. Verify the handler exists and is correctly routed:**

Check `routers/todo.py` for a handler matching thissignature:

```python
@router.get("/", response_model=list[TodoOut])
def list_todos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    todos = db.query(TodoItem).offset(skip).limit(limit).all()
    return todos
```

**Expected behavior:**
- The `@router.get("/")` decorator (not `@router.post`) registers this at `/todos/` (prefix `/todos` + path `/`).
- Query parameters `skip` and `limit` are extractedvia FastAPI's query parameter binding.
- The handler returns a list of ORM objects, which FastAPI serializes via `response_model=list[TodoOut]`.

**2. If the handler is missing, add it:**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import TodoItem
from schemas.schemas import TodoOut

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/", response_model=list[TodoOut])
def list_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    """
    List all todos with optional pagination.
    
    - **skip**: number of items to skip (default 0)
    - **limit**: max items to return (default 10)
    """
    todos = db.query(TodoItem).offset(skip).limit(limit).all()
    return todos
```

**3. If the handler exists but crashes, add error handling:**

```python
@router.get("/", response_model=list[TodoOut])
def list_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    try:
        todos = db.query(TodoItem).offset(skip).limit(limit).all()
        return todos
    except Exception as e:
        # Log the error for debugging
        print(f"Error listing todos: {e}")
        raise
```

Then run the failing tests to see the actual exception:

```bash
pytest docs/projects/fastapi-todo/probe_tests/test_get_todos.py::test_list_todos_when_empty -vv -s
```

### Verification

Once fixed, re-run the failing tests:

```bash
pytest docs/projects/fastapi-todo/probe_tests/test_get_todos.py -v
pytest docs/projects/fastapi-todo/probe_tests/test_delete_todo.py::test_deleted_item_absent_from_list -v
pytest docs/projects/fastapi-todo/probe_tests/test_lifecycle.py::test_create_list_delete_list -v
```

All 8 should pass. Additionally, manually test:

```bash
# Start the server
uvicorn main:app --reload

# In another terminal:
curl http://127.0.0.1:8000/todos/
# Expected: []

curl http://127.0.0.1:8000/todos/ -X POST -H "Content-Type: application/json" -d '{"title":"Test"}'
curl http://127.0.0.1:8000/todos/
# Expected: [{"id": 1, "title": "Test", "description": null, "status": "pending"}]

curl http://127.0.0.1:8000/todos/?skip=0&limit=1
# Expected: [{"id": 1, "title": "Test", "description": null, "status": "pending"}]
```

### Secondary Issue: Pagination Bug (test_list_todos_skip_beyond_count)

One test failure reveals a separate bug: when `skip` exceeds the number of items, the endpoint returns all items instead of an empty list.

**Current behavior:** `GET /todos/?skip=100` with 10 items returns all 10 items.  
**Expected behavior:** Should return `[]`.

This is a SQLAlchemy behavior quirk — negative or out-of-bounds offsets can cause issues. Add a guard:

```python
@router.get("/", response_model=list[TodoOut])
def list_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    todos = db.query(TodoItem).offset(max(0, skip)).limit(limit).all()
    return todos
```

This should be a separate P2 bug, but address it inthe same PR if fixing the 500 crash.