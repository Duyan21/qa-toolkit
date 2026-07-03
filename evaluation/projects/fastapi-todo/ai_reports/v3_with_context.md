# Bug Report: GET /todos/ Endpoint Returns 500 Errors and Invalid JSON

## Severity: P1

**Justification:** The GET /todos/ endpoint is a core feature of the todo API. Multiple tests fail whencalling this endpoint, making it impossible to listtodos. While CREATE, UPDATE, and DELETE operations work, the inability to retrieve the list of todos breaks a fundamental workflow and makes the system significantly less usable.

---

## What Happened

The test suite executed 38 tests with 8 failures, all related to the GET /todos/ endpoint. The failuresfall into two categories:

1. **HTTP 500 Internal Server Errors** (4 tests): The endpoint returns a 500 status code instead of 200
2. **Empty/Invalid JSON Responses** (4 tests): The endpoint returns empty response bodies that cannot be parsed as JSON

---

## Expected vs Actual

| Scenario | Expected | Actual |
|----------|----------|--------|
| `GET /todos/` with no parameters | HTTP 200 with JSON array of todos | HTTP 500 error |
| `GET /todos/` with limit parameter | HTTP 200 with JSON array | HTTP 500 error |
| `GET /todos/?skip=100&limit=10` | HTTP 200 with paginated results | Empty/no JSON body |
| `GET /todos/?status=pending` | HTTP 200 with filtered todos | HTTP 500 error |

---

## Root Cause Analysis

Based on the error patterns, there are likely two issues in the GET /todos/ endpoint implementation:

1. **500 errors suggest a server-side exception**, possibly:
   - Unhandled exception in query parameter parsing
   - Database query error
   - Missing/incorrect query parameter validation

2. **Empty response bodies suggest**:
   - The endpoint crashes after headers are sent
   - Response is being written but not properly formatted
   - Filter/pagination logic throws an unhandled exception

The consistent failure pattern across different parameter combinations indicates a fundamental issue with the endpoint implementation, not edge-case handling.

---

## Impact

- **User cannot retrieve todo list** - blocking core functionality
- **Pagination features broken** - skip/limit parameters non-functional
- **Filtering broken** - status filter parameter causes errors
- **Affected workflows**: 
  - List all todos (30% of test suite fails here)
  - Verify todo deletion (cannot list after delete)
  - Complete lifecycle operations

---

## Recommendation

### Immediate Action Required:

1. **Check server logs** for the full exception stack trace when GET /todos/ is called

2. **Add defensive error handling** to the GET /todos/ endpoint:

```python
@app.get("/todos/")
async def get_todos(skip: int = 0, limit: int = 10,status: Optional[str] = None):
    try:
        # Validate parameters
        if skip < 0:
            raise ValueError("skip must be >= 0")
        if limit < 0:
            raise ValueError("limit must be >= 0")
        
        # Build query with proper null/None handling
        query = db.todos
        
        if status:
            query = [t for t in query if t.get("status") == status]
        
        # Apply pagination
        results = query[skip : skip + limit]
        
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_todos: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

3. **Verify database/data store state** - ensure the backend is properly initialized

4. **Run GET /todos/ in isolation** with curl/Postman to capture the exact error message

5. **Add logging** to identify where the endpoint fails with different parameter combinations