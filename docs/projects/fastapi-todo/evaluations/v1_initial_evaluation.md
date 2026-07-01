# Evaluation Report — v1 Initial Evaluation

> **System:** FastAPI-CRUD-Todo
> **Evaluated by:** An Ho
> **Date started:** 2026-06-24
> **Last updated:** 2026-07-01 (Docker-readiness assessment added)
> **Status:** IN PROGRESS — will be frozen (AI evaluation)

---

## 1. Evaluation Scope

**What system:** FastAPI-CRUD-Todo — a CRUD REST API for managing todo items, built with FastAPI, SQLAlchemy, SQLite, and Pydantic v2.

**What version:** v1 (initial evaluation — no prior baseline exists)

**What triggered this evaluation:** Initial QA review to establish a baseline understanding of system quality and identify risks before any further development or use as a teaching reference.

**What was NOT in scope:** Performance testing, security penetration testing, load testing.

---

## 2. Methodology

1. **Document review** — Read README and all source files to map architecture and document quality.
2. **Feature decomposition** — Listed all API endpoints and verified each against source code.
3. **E2E trace** — Traced a single request (`POST /todos`) through every layer: routing → validation → ORM → database → response.
4. **Probe tests** — Sent targeted requests to verify specific assumptions (status field constraint, null handling, ID reuse, lifecycle flows).
5. **Dependency audit** — Compared `requirements.txt` pinned versions against installed environment and Pydantic API usage in source.
6. **Docker-readiness assessment** — Containerized the application to evaluate environment portability. Documented breakage scenarios and identified deployment gaps.

---

## 3. Risk Areas (ranked by severity)

### RISK-001: App cannot start with documented install path

**Evidence:**     Installing `requirements.txt` exactly as documented results in a startup error:
                  `pydantic.errors.ConfigError: unable to infer type for attribute "description"`.
                  Code uses `model_dump()` and `ConfigDict` (Pydantic v2 APIs); pinned version is v1.10.12.
**Severity:**     P2
**Business impact:** Anyone following the documented install path cannot run the app. Directly blocks the
                  tutorial use case the project exists to serve.
**Status:**       RESOLVED — updated dependencies during initial setup.
**Related issue:** ISS-001

---

### RISK-002: No input validation on status field

**Evidence:**     Probe test — `POST /todos {"title": "Test", "status": "xyz_random"}` → 200 accepted.
                  `status` declared as `Optional[str]` in schema with no enum constraint.
                  SQLAlchemy model stores it as plain `String` with no check constraint.
**Severity:**     P2 (tutorial) / P1 (production)
**Business impact:** Any string is accepted and stored. Downstream systems expecting
                  "pending/in-progress/done" will break silently on unexpected values.
**Assumption:**   A3 CONFIRMED — no constraint exists at schema or database layer.
**Related issue:** ISS-002

---

### RISK-003: Documentation drift between README and actual codebase

**Evidence:**     README shows flat layout (`database.py`, `models.py`, `schemas.py` at root).
                  Actual code uses subfolders (`database/`, `models/`, `schemas/`, `routers/`).
                  README file paths do not resolve to real locations.
**Severity:**     P2
**Business impact:** New contributor follows README, cannot find files. Degrades the onboarding
                  value of the project as a learning reference.
**Related issue:** ISS-003

---

### RISK-004: PUT with null title crashes server and corrupts database

**Evidence:**     Probe test U5 — `PUT /todos/{id} {"title": null}` → 500 Internal Server Error.
                  `TodoUpdate.title` is `Optional[str]` so Pydantic accepts null, writes NULL to DB.
                  `TodoOut.title: str` (non-optional) fails serialization → 500. Record permanently
                  corrupt; `GET /todos/` also returns 500 until DB manually repaired.
**Severity:**     P1
**Business impact:** Any caller sending `{"title": null}` takes down the update endpoint AND the
                  list endpoint. System-level availability risk.
**Related issue:** ISS-004

---

### RISK-005: SQLite reuses deleted IDs when table is empty

**Evidence:**     Probe test X4 — create (id=N), delete, create again → new record gets id=N
                  instead of id=N+1. `INTEGER PRIMARY KEY` without `AUTOINCREMENT`.
**Severity:**     P2
**Business impact:** External systems holding reference to deleted ID will silently resolve
                  to a new, unrelated record.
**Related issue:** ISS-005

---

### RISK-006: Database path hardcoded — not containerization-friendly

**Evidence:**     `database/database.py` hardcodes `DATABASE_URL = "sqlite:///./todo.db"`.
                  No `os.getenv()` fallback. Cannot externalize data path via Docker
                  volume or environment variable without modifying source code.
**Severity:**     P2 (tutorial) / P1 (production)
**Business impact:** Data cannot persist through container restart without code change.
                  Cannot configure different database per environment.
                  Bind mounting todo.db fails if file doesn't pre-exist on host.
**Related issue:** ISS-006
**Related debug:** docker_debug_log.md Scenario 2, 3

---

### RISK-007: .dockerignore does not exclude todo.db

**Evidence:**     `.dockerignore` does not list `todo.db`. `COPY . .` in Dockerfile
                  brings todo.db into image — whether a real database or a directory
                  artifact from a failed bind mount.
**Severity:**     P2
**Business impact:** Directory artifact from failed mount baked into image → app crash
                  that persists across rebuilds. Real database baked in → data leak.
**Related issue:** ISS-007
**Related debug:** docker_debug_log.md Scenario 3

---

## 4. Probe Test Results

### 4a. Manual Probes

| Test | Input | Expected | Actual | Result |
|------|-------|----------|--------|--------|
| Status constraint | `POST {"status": "xyz"}` | 422 | 200 OK | FAIL → RISK-002 |
| Startup with pinned deps | `pip install -r requirements.txt` | Server starts | Import error | FAIL → RISK-001 (RESOLVED) |
| Docker: no volume | `docker-compose up` (no volume) | App starts, creates todo.db | Crash: unable to open db | INVESTIGATED → see debug log |
| Docker: bind mount | `./todo.db:/app/todo.db` (no file) | Mount file | Docker creates directory → crash | FAIL → RISK-006, RISK-007 |

### 4b. Automated Probe Suite

Summary:

**Feature 1 — Create Todo:** 10 probes (C1-C10). Gaps found: empty title accepted, no length limit.
**Feature 2 — Get Single Todo:** 5 probes (G1-G5). All behave as expected.
**Feature 3 — List Todos:** 7 probes (L1-L7). Gap: no filter support.
**Feature 4 — Update Todo:** 7 probes (U1-U7). Critical: U5 null title → 500 crash (RISK-004).
**Feature 5 — Delete Todo:** 5 probes (D1-D5). All behave as expected.
**Cross-Feature Lifecycle:** 3 probes (X1-X3). Additional: X4 ID reuse confirmed (RISK-005).

### 4c. Known Gaps

| Gap | Affected Features | Risk |
|-----|------------------|------|
| No `status` enum enforcement | Create, Update | Any string accepted |
| No `title` min-length validation | Create | Empty string is valid todo |
| No DB column length constraint | Create, Update | Unbounded input to DB |
| Explicit `null` in PUT crashes endpoint | Update → cascades to List | 500 + DB corruption |
| No filtering on list endpoint | List | Cannot retrieve by status |
| Database path hardcoded | All (containerization) | Not portable across environments |
| .dockerignore incomplete | Build process | Artifacts leak into image |

---

## 5. Assumptions Resolved

| # | Assumption | Resolution |
|---|-----------|------------|
| A1 | Project is tutorial, not production | CONFIRMED — code, README, absence of prod config |
| A2 | Python 3.14 in use; `3.7+` claim outdated | CONFIRMED — verified; deps incompatible with 3.12+ |
| A3 | `status` field is free-text, no enforced values | CONFIRMED — probe test verified |
| A4 | `todo.db` not meant to be committed | UNCONFIRMED — no .gitignore entry (ISS-009) |
| A5 | No entry points beyond `uvicorn main:app` | CONFIRMED — filesystem inspection |
| A6 | App can self-create todo.db in container | CONFIRMED — SQLite creates file; issue was directory artifact from failed mount |

---

## 6. Open Questions Remaining

| # | Question | Why it matters |
|---|---------|---------------|
| Q2 | What values is `status` meant to accept? | Missing enum = bug or design choice? |
| Q3 | Is `todo.db` expected to be in `.gitignore`? | Accidental data/artifact commits possible |
| Q4 | Does this project have a maintained upstream? | Determines if findings have anywhere to go |
| Q5 | Why does README describe flat structure? | Documentation actively maintained or not? |

_Q1 (was requirements.txt updated after Pydantic v2 migration?) — ANSWERED: No. Resolved by investigation._

---

## 7. Recommendation

**Acceptable as:** Tutorial / learning reference for FastAPI, SQLAlchemy, and Pydantic v2 patterns.

**Not ready for:** Any production deployment or use as a dependency baseline without addressing:
1. **P1 — Fix ISS-004 first** — null title crash takes down multiple endpoints and corrupts data.
2. **P2 — Fix ISS-002** before adding any feature that reads or filters by status.
3. **P2 — Fix ISS-006** before any containerized deployment — hardcoded path blocks portability.
4. **P2 — Fix ISS-003** before sharing as onboarding resource.
5. **P2 — Fix ISS-007** before any Docker-based CI/CD — artifact leakage risk.

**Not ready for containerized deployment** without:
- Externalizing DATABASE_URL via environment variable (ISS-006)
- Adding todo.db to .dockerignore (ISS-007)
- Adding todo.db to .gitignore (ISS-009)

**Overall quality signal:**
- 9 findings total. 1 resolved. 8 open.
- 1 P1 (server crash + data corruption). 5 P2. 2 P3.
- Core CRUD logic is sound — risks are in schema constraints, documentation accuracy, and deployment readiness.
- No architectural change needed — all issues fixable at configuration and validation layer.

**Pending:** AI integration evaluation. v1 will be frozen after completion.