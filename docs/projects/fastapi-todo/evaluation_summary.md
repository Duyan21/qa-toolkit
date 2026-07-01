# Evaluation Summary — FastAPI-CRUD-Todo

_One file, always current. Read this first. Full detail lives in the linked documents._

---

## Current Status

Last updated: 2026-07-01 (Docker-readiness assessment added)
Evaluation cycle: v1 initial — IN PROGRESS
Overall: Acceptable as tutorial. Not production-ready.

---

## Active Risks (ranked by severity)

| ID      | Finding                                       | Severity          | Since      | Source            |
|---------|-----------------------------------------------|-------------------|------------|-------------------|
| ISS-004 | PUT null title → 500 crash                    | P1                | 2026-06-28 | Probe test U5     |
| ISS-002 | No status enum                                | P2/P1             | 2026-06-24 | Probe test        |
| ISS-006 | DB path hardcoded                             | P2/P1             | 2026-07-01 | Docker assessment |
| ISS-003 | Documentation drift                           | P2                | 2026-06-24 | README vs code    |
| ISS-005 | SQLite reuses deleted IDs                     | P2                | 2026-06-28 | Probe test X4     |
| ISS-007 | .dockerignore incomplete                      | P2                | 2026-07-01 | Docker assessment |
| ISS-008 | No Docker support                             | P3/P2             | 2026-07-01 | Docker assessment |
| ISS-009 | todo.db not in .gitignore                     | P3                | 2026-07-01 | Docker assessment |

---

## Resolved

| ID      | Finding              | Resolved in | How                                              |
|---------|----------------------|-------------|--------------------------------------------------|
| ISS-001 | Outdated deps        | v1 setup    | Updated fastapi, pydantic, sqlalchemy versions   |

---

## Trend

v1 (in progress):
- Initial pass: 5 findings (1 P1, 3 P2, 1 P2/P1). 1 resolved during setup.
- Docker assessment: 4 new findings (2 P2, 1 P3/P2, 1 P3).
- Running total: 9 findings. 1 resolved. 8 open.
- Pattern: no P0s found. Core logic sound. Risks concentrated in documentation accuracy, schema constraints, and deployment readiness.

---

## Version History

| Version | Date       | Trigger            | Report                                                                        |
|---------|------------|--------------------|-------------------------------------------------------------------------------|
| v1      | 2026-06-24 | Initial evaluation | [evaluations/v1_initial_evaluation.md](evaluations/v1_initial_evaluation.md) |

---

## Next Steps

- Complete AI integration evaluation
- Freeze v1 after completion
- Update evaluation_report v1 with Docker and AI findings
