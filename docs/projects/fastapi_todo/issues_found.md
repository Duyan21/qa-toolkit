# Issues Found

_Findings discovered during evaluation that represent bugs, gaps, or risks in the system. Each entry is self-contained so it can be filed as a ticket without reference to the evaluation document._

---

## Issue 1: Outdated dependencies in requirements.txt

**What:** The app fails to start when dependencies are installed exactly as documented. The pinned library versions in `requirements.txt` are incompatible with the actual code.

**Steps to reproduce:**
1. Clone the repo: `git clone https://github.com/lymanny/FastAPI-CRUD-Todo.git`
2. Create a clean virtual environment: `python -m venv env && .\env\Scripts\activate`
3. Install as documented: `pip install -r requirements.txt`
4. Start the server: `uvicorn main:app --reload`
5. Observe error at import time:
```
pydantic.errors.ConfigError: unable to infer type for attribute "description"
```
The app never starts.

**Root cause:** `requirements.txt` pins `pydantic==1.10.12`, but the code in [schemas/schemas.py](FastAPI-CRUD-Todo/schemas/schemas.py) uses Pydantic v2-only APIs — `model_dump()` and `ConfigDict`. These do not exist in Pydantic v1. The environment that was actually used to develop and run this project has `pydantic==2.13.4` installed (verified in `env/Lib/site-packages/`), which is never reflected in `requirements.txt`. Similarly, `fastapi==0.95.2` predates native Pydantic v2 support (introduced in FastAPI 0.100+).

| Dependency | Pinned in requirements.txt | Actually installed in env |
|---|---|---|
| pydantic | 1.10.12 | 2.13.4 |
| fastapi | 0.95.2 | unknown (not checked) |
| uvicorn | 0.22.0 | unknown |
| sqlalchemy | 2.0.21 | unknown |

**Fix applied:** None — this evaluation is read-only. Recommended fix: update `requirements.txt` to reflect the versions actually used:
```
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn>=0.23.0
sqlalchemy>=2.0.0
```
Or pin to exact working versions after a clean install into a fresh environment.

**Severity:** P2 — the app literally cannot start using the documented install path. In a production context this would be caught by CI/CD and dependency monitoring. In a tutorial context this directly blocks the learning experience the project promises to deliver.

**Note:** This class of issue is common in unmaintained open-source projects. Production applications typically use automated dependency updates (Dependabot, Renovate) and CI pipelines that run `pip install -r requirements.txt` from scratch on every PR, catching breakage early.

---

## Issue 2: No enforced values for the `status` field

**What:** The `status` field on a Todo item accepts any arbitrary string. There is no validation, enum constraint, or documented set of allowed values. A client can submit `status: "asdfgh"` and the system will store and return it without complaint.

**Steps to reproduce:**
1. Start the server (see Issue 1 for dependency fix first).
2. Send a create request with an arbitrary status:
```bash
curl -X POST http://127.0.0.1:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "status": "asdfgh"}'
```
3. Observe response: `{"id": 1, "title": "Test", "description": null, "status": "asdfgh"}` — accepted without error.

**Root cause:** The `status` field is declared as `Optional[str]` in [schemas/schemas.py:8](FastAPI-CRUD-Todo/schemas/schemas.py#L8) with no further constraint. The SQLAlchemy model in [models/models.py:10](FastAPI-CRUD-Todo/models/models.py#L10) also stores it as a plain `String` column with no database-level check constraint.

```python
# schemas/schemas.py — current
status: Optional[str] = "pending"

# what a constrained version would look like
from enum import Enum
class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in-progress"
    done = "done"

status: Optional[StatusEnum] = StatusEnum.pending
```

**Fix applied:** None — evaluation is read-only. Recommended fix: introduce a `StatusEnum` (as above) in `schemas.py` and use it as the field type. FastAPI will automatically reject invalid values with a 422 and document the allowed values in `/docs`.

**Severity:** P3 — not a crash, but a data integrity gap. Any feature built on top of `status` (filtering, UI display, workflow logic) will need to defensively handle arbitrary strings. In a learning project this is acceptable; in production it would cause silent data corruption as the set of statuses drifts across clients.

**Assumption dependency:** This finding assumes the intent was to have a bounded set of status values. If `status` is intentionally free-text (e.g. user-defined labels), this is a design choice, not a bug. See Open Question Q2 in `evaluation.md`.
