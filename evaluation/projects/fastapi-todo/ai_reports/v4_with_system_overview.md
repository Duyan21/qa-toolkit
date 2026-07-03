# Bug Report: `GET /todos/` endpoint returns 500 or invalid response

## Title
`GET /todos/` list endpoint crashes or returns malformed JSON on multiple query parameter combinations

## Severity
**P1** — Core feature broken

**Justification:** The list endpoint is a primary user-facing feature (from Section 2.1: "They check back later to see their full list of tasks" maps to `GET /todos`). 8 of 38 tests fail, all related to listing todos. The endpoint is partially functional (some paths succeed) but fails under common conditions (empty database, with pagination params, after deletions). Users cannot reliably retrieve their task list.

---

## What Happened

The probe test suite executed 38 tests against a running FastAPI-CRUD-Todo instance. **8 tests failed**, all involving the `GET /todos/` endpoint:

| Test | Failure Mode |
|------|--------------|
| `test_list_todos_when_empty` | HTTP 500 response |
| `test_list_todos_default_limit` | HTTP 500 response |
| `test_list_todos_skip_and_limit` | HTTP 500 response + JSON decode error |
| `test_list_todos_skip_beyond_count` | Incorrect return value (expected `[]`, got 10 items) |
| `test_list_todos_no_status_filter` | HTTP 500 response |
| `test_list_todos_insertion_order` | HTTP 500 response + JSON decode error |
| `test_deleted_item_absent_from_list` | JSON decode error (empty response body) |
| `test_create_list_delete_list` | JSON decode error (empty response body) |

**Common error signatures:**
- `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)` — response body is empty or not JSON
- HTTP 500 — server-side unhandled exception
- Assertion failures on return values — pagination logic not respecting `skip` parameter

---

## Expected vs Actual

### Expected behavior:
- `GET /todos/` returns HTTP 200 with JSON array of todo items
- `GET /todos/?skip=0&limit=10` returns up to 10 items, skipping the first 0
- `GET /todos/?skip=100` returns an empty array `[]` (skip beyond end of list)
- `GET /todos/` after creating and deleting items correctly omits deleted items from the list

### Actual behavior:
- `GET /todos/` (no params, empty database) → HTTP 500
- `GET /todos/?skip=0&limit=10` → HTTP 500 or empty body
- `GET /todos/?skip=100` (with 10 items in database) → HTTP 200 with all 10 items (skip parameter ignored)
- `GET /todos/` after delete → Empty response body (not valid JSON)

---

## Root Cause Analysis

Based on the test failures and the codebase structure (Section 4.1 and Section 3.2), the root cause is in [routers/todo.py](FastAPI-CRUD-Todo/routers/todo.py), likely in the `read_todos` handler. **Probable causes:**

1. **Missing or incorrect pagination query parameters** — The handler may not have defined `skip` and `limit` as query parameters with proper type hints. Without `Query(...)` wrappers or explicit parameter definitions, FastAPI may fail to parse them correctly or may not apply them at all.

2. **Unhandled exception in database query** — The `db.query()` call likely raises an exception when the table is empty or when query parameters are invalid, and there is no `try/except` block to handle it gracefully (see Section 4.1 error path note: "If `db.commit()` raises... no explicit `try/except` exists").

3. **Response serialization failure** — After a successful query, if the response list cannot be serialized through the `TodoOut` schema (e.g., due to missing `from_attributes=True`), FastAPI would return a 500. However, this is less likely since `TodoCreate` tests pass.

4. **Missing route handler or incorrect decorator** — The `GET /todos/` endpoint may not be registered at all, or it may be shadowed by the `GET /todos/{id}` route if ordering is wrong.

**To confirm, the actual `read_todos` handler code should be examined.** Based on the pattern in `create_todo` (Section 4.1), the likely implementation is:

```python
@router.get("/", response_model=list[TodoOut])
def read_todos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    todos = db.query(TodoItem).offset(skip).limit(limit).all()
    return todos
```

**Suspected defect:** if the handler uses positional `offset()` and `limit()` without the `Query()` annotation, or if it calls `offset()` before `limit()` (which can cause issues in some SQLAlchemy versions), or if the `db.query()` itself fails on an empty table, the 500 errors would occur.

---

## Impact

| Persona | Impact |
|---------|--------|
| **End user (learner)** | Cannot view their tasks after creating them. Primary use case (Section 2.1: "They check back later to see their full list") is broken. The tutorial is unusable. |
| **Instructor using this as reference material** | Students will encounter broken code and lose confidence in the project as a teaching tool. Requires workaround or manual fix before assigning. |
| **Evaluator assessing production readiness** | Confirms that the system is not production-ready. This is expected per Section 1.2 ("primarily a teaching/reference project"), but it's a blocker for even basic learning tasks. |

**Data consistency risk:** Low. CRUD operations on individual items (create, get by id, update, delete) mostly work. The list endpoint failure does not corrupt existing data, just prevents retrieval.

---

## Recommendation

### Immediate action (code fix):

Inspect and correct the `read_todos` route handler in [routers/todo.py](FastAPI-CRUD-Todo/routers/todo.py). The corrected handler should:

1. **Use explicit `Query()` parameters for pagination:**
   ```python
   from fastapi import Query
   
   @router.get("/", response_model=list[TodoOut])
   def read_todos(
       skip: int = Query(0, ge=0),
       limit: int = Query(10, ge=0),
       db: Session = Depends(get_db)
   ):
       todos = db.query(TodoItem).offset(skip).limit(limit).all()
       return todos
   ```

2. **Wrap the query in a try/except block to handle edge cases:**
   ```python
   @router.get("/", response_model=list[TodoOut])
   def read_todos(
       skip: int = Query(0, ge=0),
       limit: int = Query(10, ge=0),
       db: Session = Depends(get_db)
   ):
       try:
           todos = db.query(TodoItem).offset(skip).limit(limit).all()
           return todos
       except Exception as e:
           # Log the error and return empty list or 500 with detail
           raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
   ```

3. **Ensure the response schema has `from_attributes=True`** (already present in `TodoOut` per Section 4.1, so this is likely OK).

4. **Test with the probe test suite** to confirm all 8 failing tests pass after the fix.

### Longer-term action (documentation):

- Update [README.md](FastAPI-CRUD-Todo/README.md) to include a table of all endpoints with query parameter documentation (e.g., "`GET /todos/` supports `?skip=0&limit=10` for pagination").
- Add a note in the codebase (or a comment in `routers/todo.py`) explaining the pagination behavior.

### Verification:

After the fix, re-run the test suite and confirm:
```bash
pytest docs/projects/fastapi-todo/probe_tests/ -v
```

All 38 tests should pass.