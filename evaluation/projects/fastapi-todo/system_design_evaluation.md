# System Design Evaluation — FastAPI-CRUD-Todo

_Synthesizes [system_overview.md](system_overview.md), [issues_found.md](issues_found.md), the Docker-readiness assessment, and [ai_evaluation.md](ai_evaluation.md) into a single design-level read of the system._

---

## 1. Design Intent

FastAPI-CRUD-Todo is a **teaching artifact**, not a product. It exists to show a beginner what a minimal FastAPI + SQLAlchemy + Pydantic CRUD service looks like end to end: four endpoints (`POST`, `GET` list, `GET` one, `PUT`, `DELETE`) over a single `TodoItem` entity, backed by a local SQLite file.

- **For whom:** developers learning to build a web API with FastAPI — not internal teams, not paying customers, not any team operating it in production.
- **At what scale:** single process, single SQLite file, no auth, no multi-tenancy, effectively single-user. There is no scale target because the design goal was clarity of the CRUD pattern, not throughput, concurrency, or data isolation.
- **Explicit non-goals** (from system_overview.md §2.2): no auth/authorization, no multi-user support, no input sanitization beyond basic type validation, no deployment/production config, no migrations, no tests in the repo.

Every decision below has to be read against this intent — the system is not "badly designed," it is designed for a narrower job than production deployment, and most of its risk comes from that gap being invisible to someone who only reads the README.

---

## 2. Design Decisions + Tradeoffs

| Decision | Why it's reasonable here | Where it breaks under scale |
|---|---|---|
| **FastAPI, used only for routing + `/docs`** | Near-zero boilerplate, self-documenting API — ideal for a teaching project where the contract has to be legible without extra tooling. | Async and dependency-injection features are barely used. At real scale you'd want async DB drivers, background tasks, and structured dependency graphs — none of the scaffolding for that exists yet, so growth means re-architecting, not extending. |
| **Pydantic v2 with 3 near-duplicate schemas** (`TodoCreate`, `TodoUpdate`, `TodoOut`) | Keeps create/update/response shapes independently correct; `exclude_unset=True` makes partial updates safe. | Every new field must be added to (or deliberately excluded from) three classes by hand. No shared base schema. This is a maintenance tax that scales linearly with field count and is easy to let drift silently. |
| **SQLAlchemy + SQLite, `Base.metadata.create_all`, no migrations** | Zero setup — exactly what a tutorial needs; a learner can run it in one command. | SQLite locks the whole file on write, so it cannot support concurrent writers. There is no schema migration path — any schema change means manually dropping and recreating the table, which means manually destroying data. This is the single decision least compatible with any real deployment. |
| **No service/repository layer — router function does validation, ORM mapping, and persistence directly** (system_overview.md §4.1) | Correct simplification for a 4-field entity; adding a layer here would be over-engineering for the stated scope. | This is the exact seam that would need to be introduced first if the project ever grew past a teaching example — business rules, authorization checks, and multi-step transactions all have nowhere to live today except inside the route handler. |
| **`status` as a free-text string, no enum** (ISS-002) | Fastest path to a working field; no decision needed about the "right" set of values for a tutorial. | Any string is silently accepted (`POST /todos {"status": "xyz_random"}` → 200). Any downstream consumer — dashboard, filter, workflow — that assumes a bounded set of values breaks silently the first time unexpected data arrives. |
| **`TodoUpdate.title: Optional[str]`, but `TodoOut.title: str`** (ISS-004) | Looks reasonable in isolation — "optional" reads as "you don't have to send it." | This is the design flaw with the widest blast radius in the whole system: it lets a client legally write `NULL` into a column the read path assumes is always populated (see Section 3). |
| **No `.env`/config layer — `DATABASE_URL` hardcoded in source** (ISS-006) | One less concept for a beginner to learn; the app runs identically everywhere. | Breaks the moment you containerize or need more than one environment (dev/staging/prod) — the DB location can only change by editing source code. |
| **No auth, no per-user scoping** | Removes an entire category of complexity irrelevant to teaching CRUD. | This is a hard boundary, not a gradient — the system cannot be scaled to "more than one legitimate user" without a full identity/authorization layer added, not tuned. |

---

## 3. Failure Points — What Breaks First

Ranked by what actually gives out first if this system is pushed past its design envelope (single learner, no concurrency, no adversarial input):

1. **Data corruption cascading into total read-path outage (ISS-004, P1).** `PUT /todos/{id} {"title": null}` is accepted by `TodoUpdate` (optional field), written to SQLite as `NULL`, and then every future `GET /todos/` — including endpoints that never touched that record directly — fails with a 500 because `TodoOut.title: str` cannot serialize a `NULL`. One bad write disables the entire list/read surface until someone manually repairs the database. This is the single most severe finding in the system and the one the [AI evaluation](ai_evaluation.md) confirms an AI reviewer cannot diagnose even when handed the answer directly — because the cause lives in database state, not in code it can read.
2. **Silent data-quality drift via the unvalidated `status` field (ISS-002).** No functional crash, but the system will happily store any string. In a tutorial context this is invisible; the moment any second system (dashboard, filter, export) consumes this data assuming three known statuses, it breaks — quietly, not loudly.
3. **Concurrency failure under SQLite's file-level locking.** Not yet an observed issue in probes, but structurally guaranteed: any attempt to run more than one writer against `todo.db` at once will contend on the file lock. This is a "breaks the first time someone tries to scale it past single-user" failure, not a "breaks today" one.
4. **Docker/deployment friction (ISS-006, ISS-007, ISS-008, ISS-009).** Hardcoded DB path, incomplete `.dockerignore`, no Dockerfile in the original repo, `todo.db` not gitignored. None of these crash the app — they crash the *attempt to deploy* it. Confirmed directly in [docker_debug_log.md](docker_debug_log.md): bind-mounting `todo.db` before it exists causes Docker to create a directory instead of a file, which then crashes the app on startup.
5. **ID reuse after table empties (ISS-005, P2).** SQLite reissues a deleted row's ID once the table is empty, because `id` lacks `AUTOINCREMENT`. Low likelihood in a tutorial's usage pattern, but dangerous in any long-running system with periodic bulk deletes — any external reference (cache, audit log, bookmark) silently resolves to the wrong record.
6. **Documentation drift (ISS-003; ISS-001 resolved during setup but same root pattern — docs not maintained alongside code).** Lowest severity, but the entry point for everything else: README file paths don't match the actual code. This doesn't break the running system, but it's the first thing a new evaluator or contributor hits, and it's what makes the deeper issues (2 and beyond) harder to discover — nobody trusts a README that's already wrong about the file layout.

The pattern across all six: **the system fails quietly before it fails loudly.** Nothing here throws an error on the happy path; every failure requires either malformed input (`null` title), an unusual sequence (delete-then-create when empty), or an operational context the design never considered (Docker, concurrent writers, multiple environments).

---

## 4. SE/Evaluator Questions

**"If this were deployed for an enterprise banking customer, what fails first?"**

Authentication and data integrity fail first, and in that order. There is no authentication or authorization layer at all — every endpoint is open to anyone who can reach the port, which alone disqualifies this from any regulated environment before a single request is sent. Assuming that gap were patched, the next failure is the null-title cascade (ISS-004): a single malformed `PUT` request corrupts a record and takes down the entire read path for every user, not just the one who sent the bad request — in a banking context this reads as an availability incident with a data-integrity root cause, which is the worst combination for an audit trail. Underneath that, SQLite's single-file, file-locking model cannot support the concurrent transaction volume or the durability guarantees (backup, point-in-time recovery, replication) a banking customer would require regardless of load — this isn't a bug to fix, it's a database choice that would need to be replaced entirely (e.g. Postgres) before this system could be considered.

**"The compliance team is asking about AI output reliability — how do you answer?"**

Short answer: AI is reliable for formatting and severity triage, not for root-cause analysis. Evidence from 6 controlled tests follows.

Across six versions of increasing context — from a bare test log up to giving the AI the exact root-cause writeup verbatim — the AI correctly identified severity and structured the report every time, but it never once connected eight related test failures back to their single shared cause (a corrupted database record from an earlier write). It treated eight symptoms as eight independent bugs in all six versions, including the version where the answer was in the input text it was reading. The reason is structural, not a prompting problem: the root cause lived in *runtime state* — a bad row in the database — and the AI only ever reasons over static text (code and docs), so no amount of additional documentation could make it observe that state. For compliance purposes, that means: AI-generated reports can be trusted to correctly format and prioritize *known, already-diagnosed* issues, but any AI-authored root-cause conclusion involving more than one symptom, or involving data/state rather than pure code logic, requires mandatory human verification before it's treated as final. This is a process control we'd bake into the review workflow, not a limitation we can prompt our way out of.

---

## 5. What I Would Change

In priority order, as incremental fixes rather than a rebuild:

1. **Close ISS-004 immediately.** Change `TodoUpdate.title` from `Optional[str]` to required, or add a validator that rejects an explicit `null`; add a `NOT NULL` constraint on the `title` column as a second line of defense. This is a two-line fix that eliminates the single highest-severity, widest-blast-radius issue in the system.
2. **Add the `StatusEnum` constraint (ISS-002).** Turns silent bad data into an immediate, self-documenting 422 at the API boundary — the cheapest fix with the highest long-term data-quality payoff, and it's a one-line schema type change.
3. **Externalize `DATABASE_URL` via `os.getenv` with the current hardcoded value as the default (ISS-006).** Zero behavior change for the existing tutorial use case, but unblocks every Docker/deployment scenario at once.
4. **Add `AUTOINCREMENT` to the `id` column (ISS-005).** Trivial model change, permanently removes the ID-reuse risk.
5. **Fix `.dockerignore` and `.gitignore` to exclude `todo.db` (ISS-007, ISS-009), and ship the Dockerfile/compose files already produced during this evaluation (ISS-008).** Turns "not Docker-ready" into "Docker-ready," using artifacts that already exist rather than new work.
6. **Update the README to match the actual subfolder structure and document the data model, query params, and `status` values (ISS-003 + system_overview.md §5).** No code risk, directly fixes the first thing every new evaluator or contributor hits.
7. **Only after 1–6: introduce a thin service/repository layer separating business logic from persistence.** I'd defer this because system_overview.md is right that it would be over-engineering for the current 4-field scope — but it becomes the necessary next step the moment any business rule (e.g. status transition validation, ownership checks) needs to be added, so it belongs on the list, just last.

I would explicitly *not* start with a rewrite or a framework change — every fix above is a localized, low-risk patch to the existing design, and the design's core shape (FastAPI + SQLAlchemy + Pydantic, one entity, direct router-to-DB flow) is appropriate for what this system is for. The problem was never the architecture; it was a handful of unguarded edges within it.