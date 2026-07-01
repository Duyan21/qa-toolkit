## Section 1: Product Identity

### 1.1 What — What is this product?

An app that lets users create, view, edit, and remove personal tasks in a simple list.

### 1.2 Why — Why does it exist?

This product exists as a simple, minimal example of recording and managing tasks created by a user — primarily a teaching/reference project rather than a production app.

### 1.3 Who — Who uses it?

Beginners who are learning to build a web application with FastAPI, Python, and SQLAlchemy.

---

## Section 2: Business Perspective

### 2.1 End-to-End User Journey

A user opens the app and adds a new task they need to do. They check back later to see their full list of tasks. They look up one task to review its details. They edit a task when something about it changes (e.g. its status). They remove a task once it's no longer needed.

(Underlying this journey, each step maps to an API call: create → `POST /todos`, view list → `GET /todos`, view one → `GET /todos/{id}`, edit → `PUT /todos/{id}`, remove → `DELETE /todos/{id}` — but the journey itself should be described in the user's terms first.)

### 2.2 Product Scope & Boundaries

**Scope (what it does):**
- Users can create, view, edit, and delete tasks.
- Data persists between sessions — tasks are stored in a local database file and survive restarts.
- The API is self-documented — interactive docs are available at `/docs` without any extra setup.
- Code is organized into separate modules for routing, validation, data access, and storage.

**Boundaries (what it deliberately does NOT do):**
- No authentication or authorization — anyone with API access can read/edit/delete any task.
- No multi-user support — tasks aren't scoped to a user/owner; it's a single shared list.
- No input sanitization beyond Pydantic type validation — no length limits, no profanity/content checks.
- No deployment or production config (no Docker, no env-based settings, no migrations tool like Alembic) — `Base.metadata.create_all` only.
- No pagination defaults beyond `skip`/`limit` query params; no sorting or filtering by status.
- No tests included in the repo.

Each of these is a design choice appropriate for a learning project, but would be a gap if evaluated as production-ready software.

---

## Section 3: Technology Perspective

### 3.1 Architecture Diagram

```
Client
  │
  │  HTTP request
  ▼
main.py  ─── app entry point, mounts router at /todos
  │
  ▼
routers/todo.py  ─── handler + inline business logic
  │                          │
  │ validates input/output   │ depends on for DB session
  ▼                          ▼
schemas/schemas.py      database/database.py
(Pydantic: TodoCreate,  (get_db → SessionLocal)
 TodoUpdate, TodoOut)          │
                               ▼
                         models/models.py
                         (TodoItem ORM model)
                               │
                               ▼
                           todo.db  ─── SQLite file on disk
```

### 3.2 Codebase Structure

Actual structure (verified against the filesystem; differs from what the project's own README documents):

```
FastAPI-CRUD-Todo/
├── database/
│   └── database.py          # Engine, SessionLocal, Base, get_db dependency
├── models/
│   └── models.py             # SQLAlchemy TodoItem model
├── schemas/
│   └── schemas.py            # Pydantic schemas (TodoCreate, TodoUpdate, TodoOut)
├── routers/
│   └── todo.py                # CRUD API endpoints, mounted at /todos
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Pinned dependencies
├── todo.db                    # Generated SQLite database file
└── README.md                  # Project documentation (out of date vs. actual structure)
```

Note: the project's README describes a flat layout (`database.py`, `models.py`, `schemas.py` at the repo root), but the real code organizes each into its own subfolder. This is a documentation drift worth flagging in the evaluation — the README no longer reflects the codebase.

### 3.3 Key Technology Decisions

- **Backend: FastAPI** — defines the four CRUD endpoints under `/todos`. Chosen for its low boilerplate and built-in `/docs`, which fits a teaching project where the API contract needs to be self-explanatory; the tradeoff is that FastAPI's async/dependency-injection features (e.g. `Depends(get_db)`) go unused beyond their simplest form here.
- **Validation: Pydantic** — `TodoCreate`, `TodoUpdate`, `TodoOut` schemas in [schemas/schemas.py](FastAPI-CRUD-Todo/schemas/schemas.py). Separating create/update/out schemas lets partial updates (`exclude_unset=True`) work safely, but it also means three near-duplicate classes to keep in sync as the model grows.
- **ORM / Database: SQLAlchemy + SQLite** — single `TodoItem` table with `id`, `title`, `description`, `status`. SQLite requires zero setup, which is ideal for a tutorial, but it's not production-viable under concurrent writes (file-level locking) and has no migration story here.
- **Server: Uvicorn** (per [requirements.txt](FastAPI-CRUD-Todo/requirements.txt)) — standard, minimal ASGI server pairing for FastAPI; no production process manager (e.g. Gunicorn workers) is configured.

---

## Section 4: The Bridge — End-to-End Trace

### 4.1 One Request, Start to Finish

Tracing `POST /todos` — a user creates a new task.

```
[Request] → [Route/Handler] → [Business Logic] → [Database] → [Response]
```

1. **Request** — Client sends `POST /todos/` with JSON body, e.g.
   `{"title": "Buy milk", "description": "2%", "status": "pending"}`.

2. **Routing** — [main.py:9](FastAPI-CRUD-Todo/main.py#L9) mounted `todo.router` under prefix `/todos`, so FastAPI dispatches the request to [routers/todo.py:12-13](FastAPI-CRUD-Todo/routers/todo.py#L12-L13):
   ```python
   @router.post("/", response_model=TodoOut)
   def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
   ```

3. **Validation (entry boundary)** — Before the handler body runs, FastAPI parses the JSON body against the `TodoCreate` schema ([schemas/schemas.py:5-8](FastAPI-CRUD-Todo/schemas/schemas.py#L5-L8)). If `title` is missing or the wrong type, the request is rejected with a 422 here — the handler code never executes. `description` and `status` are optional, with `status` defaulting to `"pending"`.

4. **Dependency injection** — `Depends(get_db)` calls [database/database.py:10-15](FastAPI-CRUD-Todo/database/database.py#L10-L15), which opens a `SessionLocal()` and yields it for the duration of the request, closing it afterward regardless of outcome.

5. **Business logic** — Inside the handler ([routers/todo.py:14](FastAPI-CRUD-Todo/routers/todo.py#L14)):
   ```python
   db_todo = TodoItem(**todo.model_dump())
   ```
   The validated Pydantic object is unpacked into a SQLAlchemy `TodoItem` ORM instance ([models/models.py:5-10](FastAPI-CRUD-Todo/models/models.py#L5-L10)). There is no additional business logic (no dedupe checks, no defaults beyond what Pydantic already set) — the mapping is a direct passthrough.

6. **Database** — `db.add(db_todo)` stages the new row; `db.commit()` writes it to `todo.db` (SQLite) and assigns it an autoincrement `id`; `db.refresh(db_todo)` reloads the object from the database so `db_todo.id` is populated on the Python object ([routers/todo.py:15-17](FastAPI-CRUD-Todo/routers/todo.py#L15-L17)).

7. **Response (exit boundary)** — The handler returns `db_todo`, the raw ORM object. FastAPI serializes it through the `response_model=TodoOut` schema. This only works because `TodoOut` sets `model_config = ConfigDict(from_attributes=True)` ([schemas/schemas.py:15-16](FastAPI-CRUD-Todo/schemas/schemas.py#L15-L16)), which tells Pydantic v2 it's allowed to read attributes off a non-dict object (the ORM instance) rather than requiring a dict. The client receives `{"id": 1, "title": "Buy milk", "description": "2%", "status": "pending"}`.

**What this trace reveals about the architecture:** validation happens twice — once on the way in (`TodoCreate`) and once on the way out (`TodoOut`) — with the ORM model sitting in between as the only thing that touches persistence. There's no service/repository layer separating "business logic" from "database access"; the router function does both directly. For a 4-field CRUD app this is a reasonable simplification, but it's the seam that would need to be introduced first if this project ever grew beyond a teaching example.

**Error path:** If `db.commit()` raises (e.g. database locked, constraint violation), no explicit `try/except` exists in the handler. The exception propagates to FastAPI's default error handler and returns a 500 response to the client. The `get_db` dependency's `finally` block closes the session but does not explicitly call `db.rollback()` — SQLAlchemy will roll back automatically when the session is closed in a failed state, but this is implicit behavior, not a deliberate choice expressed in the code. Acceptable for a tutorial; production handlers would need explicit error handling and a rollback call per endpoint.

---

## Section 5: Documentation Quality Assessment

_How well does the README serve someone evaluating this system?_

### What's well documented:
- Project purpose and target audience are stated clearly in the Overview.
- Feature list (Section "Features") maps cleanly to what the code actually delivers.
- Installation steps (clone → venv → pip install → uvicorn) are complete and in correct order.
- The `/docs` endpoint is called out explicitly — important for a FastAPI project since it's the fastest way to explore the API without writing code.
- Python version requirement (`3.7+`) is stated.

### What's missing or unclear:
- **Codebase structure is out of date** — the README shows a flat layout (`database.py`, `models.py`, `schemas.py` at root) but the real code uses subfolders (`database/`, `models/`, `schemas/`). A newcomer following the README will not recognize the actual file tree.
- **No description of the data model** — the README never mentions what a Todo item looks like (`id`, `title`, `description`, `status`) or what values `status` can hold. Someone evaluating the API has to infer this from `/docs` or read the source.
- **No explanation of query parameters** — `GET /todos` supports `skip` and `limit` for pagination but this is not mentioned anywhere in the README.
- **No troubleshooting section** — the pinned dependency versions are incompatible with the code (see Section 3.4 and `issues_found.md`), and there's no guidance for when setup fails.
- **No mention of `todo.db`** — the database file is generated at runtime but is not listed in `.gitignore` and not explained in the README; evaluators may be confused whether to commit it.
- **Author bio is mismatched** — README footer says "lymanny — iOS Developer", which is incongruent with a Python/FastAPI project and may confuse readers about whether this is the primary codebase or a side learning project.

### What's mixed together that should be separated:
- **"Features" mixes product capabilities with infrastructure choices**: "CRUD Operations" (product behavior) and "SQLite Database" (infrastructure) are listed as peer items in the same bullet list, which obscures which claims are user-facing and which are implementation details.
- **Installation and environment setup are in separate sections with different headers** ("Installation" and "Create a Virtual Environment & Activate It") but describe a single continuous flow — a reader has to jump between them to understand the full setup sequence.
- **API documentation is implied, not shown** — there's a screenshot of `/docs` but no table of endpoints or request/response examples. This forces the reader to run the project just to see the API surface, rather than evaluating it from the README alone.

---

## Section 6: Quick Reference

### 6.1 How to run

```bash
# 1. Clone the repository
git clone https://github.com/lymanny/FastAPI-CRUD-Todo.git
cd FastAPI-CRUD-Todo

# 2. Create and activate a virtual environment
python -m venv env
# macOS/Linux:
source env/bin/activate
# Windows:
.\env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn main:app --reload
```

App runs at `http://127.0.0.1:8000`.
Interactive API docs at `http://127.0.0.1:8000/docs`.

> **Note:** See `issues_found.md` — the pinned versions in `requirements.txt` are incompatible with the code on newer Python environments. You may need to install updated versions manually.

### 6.2 Key endpoints / interfaces

All endpoints are prefixed with `/todos`.

| Method   | Path           | Description                                          |
|----------|----------------|------------------------------------------------------|
| `GET`    | `/`            | Health check — returns welcome message               |
| `POST`   | `/todos/`      | Create a new todo item                               |
| `GET`    | `/todos/`      | List all todos (supports `?skip=0&limit=10`)         |
| `GET`    | `/todos/{id}`  | Get a single todo by its integer id                  |
| `PUT`    | `/todos/{id}`  | Update a todo (partial update — only send changed fields) |
| `DELETE` | `/todos/{id}`  | Delete a todo by id                                  |

**Todo item shape:**
```json
{
  "id": 1,
  "title": "Buy milk",
  "description": "2%",
  "status": "pending"
}
```
`title` is required on create. `description` and `status` are optional; `status` defaults to `"pending"` (no enforced enum — any string is accepted). See **Issue 2** in [issues_found.md](issues_found.md) for the full finding and recommended fix.

### 6.3 Glossary

- **Todo item** — the single data entity in this system. Has four fields: `id` (auto-assigned integer), `title` (required string), `description` (optional string), `status` (optional string, default `"pending"`).
- **`get_db`** — FastAPI dependency in [database/database.py](FastAPI-CRUD-Todo/database/database.py) that opens a database session per request and closes it after. Injected via `Depends(get_db)` in every route handler.
- **`TodoCreate` / `TodoUpdate` / `TodoOut`** — three Pydantic schemas in [schemas/schemas.py](FastAPI-CRUD-Todo/schemas/schemas.py) that represent the incoming create payload, the incoming update payload (all fields optional), and the outgoing response shape respectively.
- **`Base.metadata.create_all`** — SQLAlchemy call in [main.py](FastAPI-CRUD-Todo/main.py) that creates the `todos` table on startup if it doesn't exist. There is no migration system; schema changes require manually dropping and recreating the table.

---

## Section 7: Assumptions Log

_Update frequency: when architecture or scope changes. Mark Status as CONFIRMED once verified by code reading or probe test, REJECTED if disproven._

| # | Assumption | Basis | Risk if wrong | Status |
|---|-----------|-------|---------------|--------|
| A1 | The project is intended as a learning/tutorial artifact, not a production deployment. | README language ("perfect for beginners"), author bio, absence of any production config. | Low — the code itself confirms this regardless of intent. | CONFIRMED |
| A2 | The actual running Python version is 3.14 (found in the local venv). The code's stated requirement is `3.7+`. | `env/pyvenv.cfg` and repro test. | Medium — the stated `3.7+` range is outdated: `requirements.txt` pins Pydantic v1.10.12, incompatible with Python 3.12+. True supported range unknown without a clean test matrix. | CONFIRMED (broken on 3.14 in repro) |
| A3 | The `status` field is intended to be a free-text string with no enforced values. | No enum constraint in model or schema. | Medium — if the intent was to enforce `pending / in-progress / done`, the missing constraint is a bug, not a design choice. | CONFIRMED (probe test — any string accepted with 200) |
| A4 | `todo.db` is not meant to be committed to version control. | No `.gitignore` entry exists in the repo to confirm or deny this. | Low — consequence is accidental data commit, not a functional gap. | UNCONFIRMED |
| A5 | The project has no other entry points or scripts beyond `uvicorn main:app`. | Only `main.py` was found at root; no `Makefile`, `scripts/`, or `Procfile`. | Low — verified by filesystem inspection. | CONFIRMED |

---

## Section 8: Open Questions

| # | Question | Why it matters |
|---|---------|---------------|
| Q1 | Was `requirements.txt` ever updated after the code was refactored to Pydantic v2 APIs? | Determines whether the mismatch was intentional (documented upgrade path) or an oversight. See `issues_found.md`. |
| Q2 | What values is `status` meant to accept? (`pending`, `done`, `in-progress`?) | If there's an intended set of values, the missing enum constraint is a bug. If it's free-text by design, it's a scope decision. |
| Q3 | Is `todo.db` expected to be in `.gitignore`? | The file exists in the repo directory and is not ignored. Without author intent, it's unclear if this is deliberate (ship with seed data) or an oversight. |
| Q4 | Does this project have a maintained upstream? | The README links to `github.com/lymanny/FastAPI-CRUD-Todo`. If the upstream is active, open issues may already document the dependency problem. If abandoned, the evaluation findings have nowhere to go. |
| Q5 | Why does the README describe a flat file structure when the code uses subfolders? | Either the code was reorganized after the README was written, or the README was copied from a different version. Clarifying this indicates whether the documentation is actively maintained. |
