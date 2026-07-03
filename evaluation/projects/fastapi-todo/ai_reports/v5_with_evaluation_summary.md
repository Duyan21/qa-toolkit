# Bug Report: GET /todos Endpoint Returns 500 on Empty Database or With Query Parameters

## Title
`GET /todos/` returns HTTP 500 instead of 200 when database is empty or query parameters are supplied

---

## Severity
**P1** — Core feature broken

**Justification:**
- The `GET /todos/` endpoint is a primary user journey ("view full list of tasks" per Section 2.1).
- It fails consistently in two common scenarios: (1) app startup with no data, (2) pagination queries.
- 8 of 38 probe tests fail, all traceable to this endpoint.
- Current system health notes this is not a P0 because the endpoint doesn't crash the app itself, but it's a P1 because the endpoint is unusable.

---

## What Happened

When the test suite ran, **8 tests failed**—all attempting to call `GET /todos/` with various payloads:

1. **`test_list_todos_when_empty`** — Calls `GET /todos/` on a fresh database → HTTP 500
2. **`test_list_todos_default_limit`** — Calls `GET /todos/` with no params → HTTP 500
3. **`test_list_todos_skip_and_limit`** — Calls `GET /todos/?limit=1000` → HTTP 500 (JSON decode error)
4. **`test_list_todos_skip_beyond_count`** — Calls `GET /todos/?skip=1000&limit=10` → HTTP 500 or unexpected data
5. **`test_list_todos_no_status_filter`** — Calls `GET /todos/?status=pending` → HTTP 500
6. **`test_list_todos_insertion_order`** — Calls `GET /todos/` → HTTP 500 (JSON decode error)
7. **`test_deleted_item_absent_from_list`** — Calls `GET /todos/` after delete → JSON decode error (empty response body)
8. **`test_create_list_delete_list`** — Calls `GET /todos/` in lifecycle → JSON decode error

**Error patterns:**
- Most failures: HTTP 500 response with no JSON body (causes `JSONDecodeError: Expecting value: line 1 column 1`).
- One failure: HTTP 500 status code asserted instead of 200.
- One failure: unexpected data returned (skip parameter ignored).

---

## Expected vs Actual

| Scenario | Expected | Actual |
|----------|----------|--------|
| `GET /todos/` on empty DB | HTTP 200, JSON array `[]` | HTTP 500, empty response body |
| `GET /todos/?limit=10` | HTTP 200, JSON array of todos (up to 10 items) | HTTP 500, empty response body |
| `GET /todos/?skip=100&limit=10` | HTTP 200, JSON array (items 100–109, or `[]` if insufficient) | HTTP 500 or HTTP 200 with all items (skip ignored) |
| `GET /todos/?status=pending` | HTTP 200, JSON array of pending todos | HTTP 500, empty response body |

---

## Root Cause Analysis

**The endpoint is crashing internally but not returning a proper error response.**

Based on the code architecture (Section 4.1 and [routers/todo.py](FastAPI-CRUD-Todo/routers/todo.py)), the `GET /todos/` handler likely has one of these issues:

### Hypothesis 1: Query Parameter Parsing Failure ✓ **MOST LIKELY**

The endpoint accepts `skip` and `limit` query parameters (mentioned in Section 6.2), but:
- **No handler found in provided code** — The README documents `?skip` and `limit` support, but no endpoint definition was shown that parses these.
- **If parameters are defined** but have an incorrect type hint or default (e.g., `skip: int = None` instead of `skip: int = 0`), Pydantic will reject invalid types at startup or request time, raising an unhandled exception.
- **If a filter by `status` is attempted** but not implemented, the handler would crash when trying to access an undefined variable.

### Hypothesis 2: Database Query Crash on Empty Result ✓ **PLAUSIBLE**

If the endpoint does something like:
```python
@router.get("/")
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(TodoItem).all()
    return todos  # This part is fine
```
…the code itself is correct. But if it does:
```python
def get_todos(db: Session = Depends(get_db), status: str):  # <-- required param, no default
    todos = db.query(TodoItem).filter_by(status=status).all()
    return todos
```
Then calling without `?status=x` will trigger Pydantic validation to fail, returning 422, not 500. A 500 suggests an **unhandled exception in the handler body itself**, not validation.

### Hypothesis 3: Missing or Misconfigured `response_model` ✓ **POSSIBLE**

If the endpoint is missing `response_model=List[TodoOut]`, FastAPI may fail to serialize the ORM objects back to JSON. However, this usually results in a 422 (unserializable) or a clear error message, not a silent 500 with an empty body. This is less likely.

### Hypothesis 4: Database Session Corruption or Closed Session ✓ **LESS LIKELY**

If `get_db` closes the session too early (e.g., in a middleware before the endpoint returns), querying the closed session would raise an exception. However, the `finally` block in `get_db` is designed to close *after* the endpoint returns, so this would only occur if there's a race condition or middleware misconfiguration.

---

## Current System Health Context

This finding **aligns with existing risk landscape:**

- **ISS-006** ("DB path hardcoded") and **ISS-007** (".dockerignore incomplete") suggest environmental configuration gaps that could cause silent failures when the DB is not accessible.
- **ISS-002** ("No status enum") suggests the codebase may have undocumented query parameters (`?status=`) that are either unimplemented or crash on unknown values.
- The fact that **30 of 38 tests pass** (78%) indicates the core CRUD logic (create, update, delete) works; the failure is isolated to the **read/list endpoint**, which is the least tested endpoint in the provided code snippets.

---

## Impact

- **User-facing:** Any user attempting to view their task list (Section 2.1, step 2: "They check back later to see their full list of tasks") will see an error.
- **Cascading:** Workflows that depend on listing (e.g., a UI that loads the task list on app start) cannot function.
- **Testing:** The endpoint cannot be validated in integration or acceptance tests.
- **Credibility:** A 500 error on a core CRUD endpoint undermines confidence in the entire project, even though create/update/delete work.

---

## Recommendation

### Immediate (P1 — Block Release)

1. **Inspect the actual `GET /todos/` handler code** (not provided in the system overview) for:
   - Query parameter definitions and defaults (`skip`, `limit`, `status`).
   - Unhandled exceptions in the query logic.
   - Missing `response_model` annotation.

2. **Enable server-side error logging** to capture the actual exception. Add to [routers/todo.py](FastAPI-CRUD-Todo/routers/todo.py):
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   @router.get("/", response_model=List[TodoOut])
   def get_todos(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
       try:
           todos = db.query(TodoItem).offset(skip).limit(limit).all()
           return todos
       except Exception as e:
           logger.exception("Error in GET /todos")
           raise
   ```

3. **Add the missing endpoint definition** if it doesn't exist. Based on the README claiming `?skip` and `?limit` support, the handler should be:
   ```python
   from typing import List
   
   @router.get("/", response_model=List[TodoOut])
   def get_todos(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
       """
       List all todos with optional pagination.
       
       - skip: number of items to skip (default 0)
       - limit: maximum items to return (default 10)
       """
       return db.query(TodoItem).offset(skip).limit(limit).all()
   ```

4. **Remove unsupported query parameters** (e.g., `status` filter) from the README if not implemented, or implement them:
   ```python
   @router.get("/", response_model=List[TodoOut])
   def get_todos(
       db: Session = Depends(get_db),
       skip: int = 0,
       limit: int = 10,
       status: Optional[str] = None  # New parameter
   ):
       query = db.query(TodoItem)
       if status:
           query = query.filter_by(status=status)
       return query.offset(skip).limit(limit).all()
   ```

### Follow-up (P2 — Prevent Recurrence)

5. **Add unit tests for the GET endpoint** (noted as missing in Section 2.2: "No tests included in the repo"). The probe tests already exist; integrate them into the repo's CI/CD.

6. **Document the endpoint in the README** with actual examples:
   ```markdown
   #### GET /todos/
   List all todos with pagination.
   
   **Query Parameters:**
   - `skip` (integer, default 0): Skip first N todos
   - `limit` (integer, default 10): Return at most N todos
   
   **Example:**
   ```
   GET /todos/?skip=0&limit=5
   ```
   Response:
   ```json
   [
     {"id": 1, "title": "Buy milk", "description": "2%", "status": "pending"},
     ...
   ]
   ```
   
---

## Testing to Verify Fix

After applying the recommendation, run:
```bash
pytest docs/projects/fastapi-todo/probe_tests/test_get_todos.py -v
```

All 7 tests in that file should pass:
- ✓ `test_list_todos_when_empty`
- ✓ `test_list_todos_default_limit`
- ✓ `test_list_todos_skip_and_limit`
- ✓ `test_list_todos_skip_beyond_count`
- ✓ `test_list_todos_no_status_filter`
- ✓ `test_list_todos_insertion_order`

And the dependent lifecycle tests should pass:
- ✓ `test_deleted_item_absent_from_list`
- ✓ `test_create_list_delete_list`