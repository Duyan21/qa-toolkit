# Quality Report — FastAPI-CRUD-Todo

> Audience: PM / Tech Lead / anyone deciding next steps
> Read time: 5 minutes
> Full evidence: see evaluation/ folder

## Bottom Line

This system is **acceptable as a tutorial, not production-ready**. The biggest risk isn't any single bug — it's that one malformed request (`PUT` with a null title) silently corrupts the database and cascades into a total read-path outage, and neither AI-assisted review nor casual testing would catch it before a user does. Recommendation: fix the null-title cascade (ISS-004) before anything else ships, and treat AI-generated bug reports as a formatting/triage aid only — not a substitute for human root-cause review — until a real review process is in place.

---

## 3 Key Insights

### Insight 1: One bad write takes down the entire read path

**Observation:** `PUT /todos/{id}` with `{"title": null}` is accepted (title is `Optional[str]` on the update schema), writes `NULL` into a column the response schema declares as always-present (`str`), and corrupts that database row. Every subsequent `GET /todos/` — not just requests to that one record — then fails with a 500, because the list endpoint cannot serialize the corrupted row. (Source: [ISS-004](issues_found.md), P1.)

**So what:** This isn't "one endpoint crashes." It's "one malformed request from any client, by accident or otherwise, takes down read access for every user until someone manually repairs the database." That's a system-level availability incident triggered by a single bad input — the most severe finding in the evaluation.

**Action:** Change `TodoUpdate.title` to a required field (or add a validator rejecting explicit `null`), and add a `NOT NULL` constraint on the `title` column as a second line of defense. Two small code changes; owner: whoever holds the codebase, before any further use of this app beyond local learning. Not a redesign — a same-day fix.

### Insight 2: AI cannot find cascade bugs, even with full context

**Observation:** Across 6 versions of a controlled prompt-iteration test — from a bare test-failure log up to giving the AI the full root-cause write-up (ISS-004) verbatim — the AI treated 8 related test failures as 8 independent bugs in all 6 versions. More context steadily improved formatting, severity judgment, and code-path references, but never produced cascade awareness, even when the answer was present in the input text it was reading. (Source: [ai_evaluation.md](ai_evaluation.md).)

**So what:** The team cannot rely on AI for root-cause analysis whenever failures might be related — which is exactly the failure mode Insight 1 represents. The AI only reasons over static text (code, docs); the root cause here lived in database state, which no amount of documentation makes visible to it. Trusting an AI-authored root cause on a multi-failure incident risks shipping the wrong fix while the real cause stays live.

**Action:** Require mandatory human review of any AI-generated bug report before acting on it, specifically when multiple failures appear together or the report lists several unranked "probable causes." AI output stays useful for formatting raw logs and for severity triage — those held up reliably across all 6 versions — but root-cause conclusions need a human sign-off step added to the review workflow now, not after the next incident.

### Insight 3: The system fails quietly before it fails loudly

**Observation:** Every issue found in this evaluation — the null-title cascade, the unvalidated `status` field, SQLite's ID reuse, the Docker deployment blockers — is invisible on the happy path. Nothing here throws an error under normal, well-formed use. Each one only surfaces with malformed input, an unusual sequence of operations, or an operational context (containerization, concurrent writers) the original design never anticipated. (Source: [system_design_evaluation.md](system_design_evaluation.md), Section 3.)

**So what:** Normal manual testing and demo usage will not reveal any of these risks — the app looks completely fine until someone (a user, an integrator, or an attacker) does something slightly outside the expected path. That means the team's confidence in "it works" from everyday use is not evidence that it's safe; the gap only shows up in a targeted, adversarial probe.

**Action:** Adopt recurring probe testing (edge cases, malformed input, Docker/deploy scenarios) as a standing quality practice, not a one-time pre-release pass. The probe suite already built for this evaluation ([tests/probes/fastapi-todo/](../../../tests/probes/fastapi-todo/)) is the starting point — extend it and run it whenever the code changes, rather than treating it as a one-off audit artifact.

---

## System Health Snapshot

_As of 2026-07-01 (last update to evaluation_summary.md)._

- **Overall status:** Acceptable as tutorial. Not production-ready.
- **Findings:** 9 total — 1 resolved, 8 open (1 P1, 5 P2, 2 P3). No P0s found; core CRUD logic is sound.
- **Top active risk:** ISS-004 (PUT null title → 500 cascade), P1 — the only P1 in the system.
- **Trend:** Initial evaluation pass surfaced 5 findings; a follow-up Docker-readiness assessment added 4 more. Risk is concentrated in three areas: documentation accuracy, missing schema constraints, and deployment readiness — not in the core request-handling logic itself.
- **Coverage so far:** Code quality review, probe testing (CRUD lifecycle + edge cases), Docker-readiness assessment, and a 6-version AI-output reliability study. See [evaluation_summary.md](evaluation_summary.md) for the live risk register.

---

## What's NOT in This Report

- **Load/concurrency testing.** SQLite's file-locking behavior under concurrent writers is flagged as a structural risk (system_design_evaluation.md §3) but has not been measured — no benchmark or stress test has been run.
- **Security review.** No authentication/authorization exists in this system by design (it's a tutorial), so a security assessment in the traditional sense (auth bypass, injection, etc.) was out of scope. This report does not claim the system is secure — only that auth is absent by design.
- **Full Docker/production deployment validation.** The Docker-readiness assessment identified blockers and produced a working Dockerfile/compose setup during evaluation, but this hasn't been validated against a real staging/production environment.
- **Long-running / soak testing.** All findings come from targeted probe tests and short-lived sessions; behavior under sustained use (DB file growth, long-lived connections) is untested.
- **AI evaluation beyond bug-report generation.** The AI reliability findings (Insight 2) are specific to one AI-assisted workflow (test-failure → bug report). They should not be generalized to other AI use cases (e.g. code generation, code review) without separate evaluation.
- **Next step recommendation:** if this system is being considered for anything beyond its current tutorial use, the priority order should be (1) close ISS-004, (2) run a concurrency/load test against SQLite before deciding whether a database migration is needed, (3) do a formal security review once/if auth is added.
