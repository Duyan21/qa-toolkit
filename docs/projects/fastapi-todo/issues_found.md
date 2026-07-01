# Issues Found — FastAPI-CRUD-Todo

_Append-only. Never delete entries. Same issue reappearing across versions = systemic problem, not duplicate. New joiners read this to understand system evolution._

---

## Severity Definitions

| Level | Meaning                          | Action            |
|-------|----------------------------------|-------------------|
| P0    | System unusable, no workaround   | Must fix now      |
| P1    | Core feature broken              | Fix before release|
| P2    | Non-critical, affects experience | Fix when possible |
| P3    | Minor, cosmetic                  | Optional          |

---

## ISS-001: Outdated dependencies in requirements.txt

Status:    RESOLVED in v1 (fixed during initial setup)
Found:     v1, 2026-06-24
Severity:  P2
Evidence:  App fails to start on Python 3.14. `requirements.txt` pins
           `pydantic==1.10.12` but the code uses Pydantic v2-only APIs
           (`model_dump()`, `ConfigDict`). Error at import time:
           `pydantic.errors.ConfigError: unable to infer type for attribute "description"`
Impact:    Anyone following the documented install path cannot run the app.
           Blocks the learning experience the project promises to deliver.
Resolution: Updated fastapi 0.95.2→0.137.0, pydantic 1.10.12→2.13.4,
            sqlalchemy 2.0.21→2.0.50. Migrated schemas to Pydantic v2 syntax.

---

## ISS-002: No enum constraint on status field

Status:    OPEN
Found:     v1, 2026-06-24
Severity:  P2 (tutorial context) / P1 (production context)
Evidence:  POST /todos with `{"title": "Test", "status": "xyz_random"}` → 200 accepted.
           Any string stored without validation. No constraint in schema or ORM model.
Impact:    Downstream consumers (dashboards, filters, workflow logic) expecting
           a bounded set of values ("pending" / "in-progress" / "done") will
           break silently on unexpected strings.
Fix:       Not applied — evaluation is read-only. Recommended: introduce
           `StatusEnum(str, Enum)` in schemas.py and use as field type.
           FastAPI will auto-reject invalid values with 422 and document
           allowed values in /docs.
Linked to: Assumption A3 (CONFIRMED — probe test verified no constraint exists)

---

## ISS-003: Documentation drift — README vs actual codebase structure

Status:    OPEN
Found:     v1, 2026-06-24
Severity:  P2
Evidence:  README describes flat layout: `database.py`, `models.py`, `schemas.py`
           at repo root. Actual code uses subfolders: `database/`, `models/`,
           `schemas/`, `routers/`. File paths in README do not resolve.
Impact:    New contributor follows README, cannot find files. Reduces
           onboarding value of the project as a learning reference.
Fix:       Not applied — evaluation is read-only. Recommended: update README
           structure section to reflect actual subfolder layout.
Linked to: ISS-001 (same root cause — documentation not maintained alongside code changes)

---

## ISS-004: PUT /todos/{id} with explicit null title crashes the server (500)

Status:    OPEN
Found:     v1, 2026-06-28
Severity:  P1
Evidence:  Probe test U5 — `PUT /todos/{id} {"title": null}` → 500 Internal Server Error.
           Crash chain: `TodoUpdate.title` is `Optional[str]` so Pydantic accepts `null`
           and SQLAlchemy writes `NULL` to the `title` column. FastAPI then tries to
           serialize the response using `TodoOut.title: str` (non-optional) — fails with
           an unhandled serialization error. Response body is plain text "Internal Server
           Error", not JSON. The record is now permanently corrupt in the DB.
Impact:    Any caller that sends `{"title": null}` — whether by mistake or malformed
           client — takes down the update endpoint for that record. After the crash,
           `GET /todos/` also returns 500 because the list endpoint cannot serialize
           the corrupt record, effectively making the entire read path unavailable until
           the DB is manually repaired. This is a system-level availability risk.
Fix:       Not applied — evaluation is read-only. Recommended: change `TodoUpdate.title`
           from `Optional[str]` to `str` (non-optional), or add a Pydantic validator
           that rejects explicit null on update. Also add a NOT NULL constraint on the
           `title` column at the SQLAlchemy model level as a second line of defence.

---

## ISS-005: SQLite reuses deleted IDs when table is empty

Status:    OPEN
Found:     v1, 2026-06-28
Severity:  P2
Evidence:  Probe test X4 — create todo (id=N), delete it (table now empty), create again.
           New record receives id=N instead of id=N+1. Root cause: `id` column is declared
           as `INTEGER PRIMARY KEY` without `AUTOINCREMENT`. Without that keyword, SQLite
           picks `max(id) + 1`, which resets to 1 when the table is empty.
Impact:    Any external system (client cache, audit log, bookmark) holding a reference to
           a deleted ID will silently resolve to a new, unrelated record after the table
           empties and refills. Hard to reproduce in production but dangerous in long-running
           systems with periodic bulk deletes.
Fix:       Not applied — evaluation is read-only. Recommended: add `autoincrement=True`
           to the `id` column definition in `models.py`. SQLAlchemy maps this to
           `INTEGER PRIMARY KEY AUTOINCREMENT`, which forces SQLite to use a monotonically
           increasing sequence and never reuse a previously assigned ID.

---

## Docker-Readiness Assessment (Week 8, 2026-07-01)

| Item | Status | Finding |
|------|--------|---------|
| Dockerfile exists | ❌ → ✅ | Not in original repo. Created during evaluation |
| docker-compose.yml | ❌ → ✅ | Not in original repo. Created during evaluation |
| .dockerignore | ⚠️ | Exists but does not exclude todo.db |
| requirements.txt pinned | ✅ | All 4 deps pinned correctly |
| Env vars externalized | ❌ | DATABASE_URL hardcoded in source code |
| DB path configurable | ❌ | Hardcoded "sqlite:///./todo.db" |
| Health check endpoint | ✅ | GET / returns welcome message |
| Secrets in image | ✅ N/A | No secrets in this project |
| .gitignore covers todo.db | ❌ | Not listed |

---

## ISS-006: Database path hardcoded — not Docker-friendly

Status:    OPEN
Found:     v1, 2026-07-01, Docker-readiness assessment
Severity:  P2 (tutorial) / P1 (production)
Evidence:  `database/database.py` hardcodes
           `DATABASE_URL = "sqlite:///./todo.db"`.
           No `os.getenv()` fallback. Cannot change database
           location via environment variable without modifying
           source code.
Impact:    Data cannot persist through container restart without
           code change. Cannot point to different database per
           environment (dev/staging/prod). Bind mounting todo.db
           fails if file doesn't pre-exist — Docker creates
           directory instead of file, causing app crash.
Related:   docker_debug_log.md Scenario 2, 3
Recommendation:
```python
# Current (hardcoded):
DATABASE_URL = "sqlite:///./todo.db"

# Recommended (configurable):
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")
```

---

## ISS-007: .dockerignore does not exclude todo.db

Status:    OPEN
Found:     v1, 2026-07-01, Docker-readiness assessment
Severity:  P2
Evidence:  `.dockerignore` exists but does not list `todo.db`.
           `COPY . .` in Dockerfile brings todo.db into image —
           whether it's a real database file or a directory
           artifact from a failed bind mount.
Impact:    Directory artifact from failed bind mount gets baked
           into image → app crash inside container with
           "unable to open database file" that persists across
           rebuilds. Real database file in image → development
           data leaks into every container.
Related:   docker_debug_log.md Scenario 3

---

## ISS-008: No Docker support in original repo

Status:    OPEN
Found:     v1, 2026-07-01, Docker-readiness assessment
Severity:  P3 (tutorial) / P2 (starter template)
Evidence:  Original repo contains no Dockerfile, no
           docker-compose.yml, no Docker documentation in README.
Impact:    Cannot containerize without writing config from scratch.
           Contributor must understand app internals (hardcoded
           paths, SQLite file behavior) before containerization
           is possible.
Recommendation: Acceptable for tutorial scope. Would need
           Dockerfile + compose + .dockerignore before use
           as a team starter template.

---

## ISS-009: todo.db not in .gitignore

Status:    OPEN
Found:     v1, 2026-07-01, Docker-readiness assessment
Severity:  P3
Evidence:  No `.gitignore` entry for `todo.db`. Database file
           or directory artifact from Docker can be accidentally
           committed to version control.
Impact:    Development data or corrupted artifacts could enter
           repo history permanently.
Linked to: Assumption A4 (UNCONFIRMED — author intent unknown)

---

## Issue Summary

| ID | Title | Severity | Status | Found |
|----|-------|----------|--------|-------|
| ISS-001 | Outdated deps | P2 | RESOLVED | 2026-06-24 |
| ISS-002 | No status enum | P2/P1 | OPEN | 2026-06-24 |
| ISS-003 | Documentation drift | P2 | OPEN | 2026-06-24 |
| ISS-004 | PUT null title → 500 | P1 | OPEN | 2026-06-28 |
| ISS-005 | SQLite reuses deleted IDs | P2 | OPEN | 2026-06-28 |
| ISS-006 | DB path hardcoded | P2/P1 | OPEN | 2026-07-01 |
| ISS-007 | .dockerignore incomplete | P2 | OPEN | 2026-07-01 |
| ISS-008 | No Docker support | P3/P2 | OPEN | 2026-07-01 |
| ISS-009 | todo.db not in .gitignore | P3 | OPEN | 2026-07-01 |

**Total: 9 issues. 1 resolved. 8 open (1 P1, 5 P2, 2 P3).**