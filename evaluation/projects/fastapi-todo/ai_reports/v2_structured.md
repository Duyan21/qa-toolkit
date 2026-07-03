=== VERSION 2 ===
# Bug Report: GET /todos Endpoint Returning 500 Internal Server Error

## Severity
**P1** - Critical

## What Happened
The test suite for a FastAPI TODO application is failing with 8 test failures out of 38 tests. The primary issue is that the GET `/todos` endpoint is returning HTTP 500 (Internal Server Error) responses, causing multiple tests to fail when attempting to retrieve the list of todos. Additionally, some tests fail with JSON decode errors when the response body is empty.

## Expected vs Actual

**Expected:**
- GET `/todos` endpoint should return HTTP 200 with a valid JSON array of todo items
- GET `/todos?limit=X&skip=Y` should support pagination parameters
- GET `/todos?status=<status>` should support status filtering
- All responses should contain valid JSON

**Actual:**
- GET `/todos` endpoint returns HTTP 500 (Internal Server Error)
- Empty response bodies causing `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`
- Pagination and filtering tests fail due to the 500 error

## Failing Tests
1. `test_list_todos_when_empty` - 500 error on basic GET
2. `test_list_todos_default_limit` - 500 error on basic GET
3. `test_list_todos_skip_and_limit` - 500 error + JSON decode error
4. `test_list_todos_skip_beyond_count` - Returns all items instead of emptylist
5. `test_list_todos_no_status_filter` - 500 error
6. `test_list_todos_insertion_order` - 500 error + JSON decode error
7. `test_deleted_item_absent_from_list` - JSON decode error (empty response)
8. `test_create_list_delete_list` - JSON decode error (empty response)

## Root Cause Analysis

The issue appears to be in the **GET `/todos` endpoint implementation**:

1. **Unhandled Exception in List Endpoint**: The endpoint is throwing an unhandled exception resulting in a 500 error, likely caused by:
   - Database/ORM initialization issues
   - Missing or incorrect query parameters handling
   - Unhandled null/None values in filtering logic
   - Missing exception handling for edge cases

2. **Pagination/Filtering Logic Defect**: The `test_list_todos_skip_beyond_count` test shows that when skipping beyond the total count, the endpoint returns all items instead of an empty list, indicating the skip/limit logic isnot implemented correctly.

3. **Empty Response Bodies**: Several tests receive completely empty response bodies (not even `[]`), suggesting the response serialization is failing.

## Recommendations

1. **Immediate Actions:**
   - Enable server-side logging to capture the 500 error stack trace
   - Check the application logs for exception details in the GET `/todos` endpoint
   - Verify database connectivity and migrations are applied

2. **Code Review:**
   - Review the GET `/todos` endpoint implementation for unhandled exceptions
   - Verify pagination logic correctly handles `skip` and `limit` parameters
   - Ensure status filtering handles None/missing filter values gracefully
   - Add proper error handling and validation for query parameters

3. **Testing:**
   - Add unit tests for the todos listing function with various edge cases
   - Test with empty database state
   - Test pagination boundary conditions (skip >= total count)
   - Verify response format is always valid JSON

4. **Code Quality:**
   - Add try-catch blocks in endpoint handlers
   - Return appropriate HTTP status codes with error details
   - Add input validation decorators for query parameters