# QA Evaluation Toolkit

[![QA Toolkit Tests](https://github.com/Duyan21/qa-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/Duyan21/qa-toolkit/actions/workflows/test.yml)

A QA evaluator's working portfolio — reusable diagnostic tools, a repeatable
evaluation methodology, and a full case study applying both to a real system.

**What makes this different:** every tool here exists to support a structured
evaluation practice, not just to automate tests. The case study evaluates a
system I didn't build — 9 findings across code quality, Docker-readiness, and
AI output reliability — using probe tests, environment debugging, and a
multi-version comparison of AI-generated bug reports graded against
expert-written analysis.

## Key findings (fastapi-todo case study)

- **P1 — Server crash + data corruption:** PUT with null title crashes the
  endpoint AND corrupts the database record, cascading to break the entire
  read path until the DB is manually repaired.
- **9 issues total** across code quality (3), documentation accuracy (2), and
  Docker-readiness (4) — all fixable without architectural change.
- **AI evaluation:** Claude generates professional-looking bug reports but
  misses cascade effects — treats 8 failure symptoms as 8 separate bugs
  instead of tracing to 1 root cause. Structured context improves output
  quality measurably, but human verification remains essential for
  root cause analysis.

Start at
[evaluation_summary.md](evaluation/projects/fastapi-todo/evaluation_summary.md)
for the current status — active risks, resolved issues, and version history.

## Evaluation

The methodology is project-agnostic and lives in `evaluation/frameworks/`:

| Framework | Purpose |
|---|---|
| [system_overview_template.md](evaluation/frameworks/system_overview_template.md) | Map a new system's architecture before evaluating it |
| [evaluation_report_template.md](evaluation/frameworks/evaluation_report_template.md) | Structure for a full evaluation report — scope, risks, probe results, recommendation |
| [ai_evaluation_framework.md](evaluation/frameworks/ai_evaluation_framework.md) | Generic criteria for scoring AI output quality — correctness, hallucination, failure modes, when not to trust it |

The fastapi-todo case study applies all three frameworks:

| Document | What it covers |
|---|---|
| [system_overview.md](evaluation/projects/fastapi-todo/system_overview.md) | 3-layer analysis: domain, technical, documentation quality |
| [issues_found.md](evaluation/projects/fastapi-todo/issues_found.md) | 9 issues, append-only, severity-ranked (1 P1, 5 P2, 2 P3) |
| [v1_initial_evaluation.md](evaluation/projects/fastapi-todo/evaluations/v1_initial_evaluation.md) | Full evaluation report with probe results and recommendation |
| [docker_debug_log.md](evaluation/projects/fastapi-todo/docker_debug_log.md) | 3 real breakage scenarios: what I saw vs what actually broke |
| [ai_evaluation.md](evaluation/projects/fastapi-todo/ai_evaluation.md) | AI output evaluation — prompt iteration, failure modes, when not to trust |

Probe tests that back the findings live in
[tests/probes/fastapi-todo/](tests/probes/fastapi-todo/) — they hit a running
instance of the target app, not mocks (see [Testing](#testing)).

## Tools

### log_reader / log_watcher

`log_reader.py` parses a static application log file and summarizes ERROR lines
by type and frequency. Useful for post-deployment checks and incident investigation.

```
Total error occurrences: 5
 - Database connection failed: timeout (x3)
 - Auth service unreachable (x2)
```

`log_watcher.py` monitors a live log file in real time (tail-mode). Fires an alert
when error frequency exceeds a configurable threshold within a sliding time window,
prints periodic summaries, and generates a session report on exit.

```
--- File log: live_app.log ---
Started at: 2025-05-14 10:00:00
🚨 ALERT: 5 errors in 60 seconds
   From: 10:00:05 → 10:00:58
--- Summary at 2025-05-14 10:01:00 ---
Total errors: 7
  - Database connection failed: timeout (x4)
  - Auth service unreachable (x3)
```

Pair with `log_generator.py` to simulate a live app writing randomized log entries.

### json_diff

Compares two JSON files recursively and groups results into four buckets:
missing in production, extra in production, different values, and identical.
Useful for verifying API contract consistency across environments
(e.g. staging vs production).

```
Summary — identical: 3  |  different: 1  |  missing in production: 1  |  extra in production: 0

Missing in production (1):
  - $.last_login: staging='2024-01-15'

Different (1):
  ~ $.role: staging='admin' vs production='viewer'

Identical (3):
  = $.user_id: 1001
  = $.email: 'an.ho@company.com'
  = $.status: 'active'

-> Runbook: runbooks/debug-json-mismatch.md
```

### api_checker + api_log_analyzer

Checks API health across multiple endpoints — status code, response time, and
field count. Writes results to a log file, then generates a summary report.

```
Total API checks: 3
Passed ✅: 0
Slow ⚠️: 3  (threshold: 500ms)
Failed ❌: 0
=== Slow APIs ⚠️ ===
 - https://api.github.com/users/torvalds (Response time: 922 ms)
 - https://api.github.com/repos/facebook/react (Response time: 955 ms)
 - https://jsonplaceholder.typicode.com/users/1 (Response time: 1348 ms)
```

### ai_bug_reporter

Feeds a test-failure log to Claude and drafts a bug report at one of three
escalating context levels (`v1` bare failure only → `v3` failure + system
context + severity guide). Backs the AI output evaluation in
[ai_evaluation.md](evaluation/projects/fastapi-todo/ai_evaluation.md) — the
`ai_reports/` folder holds the raw graded outputs.

```bash
# Requires Anthropic API key — get one at https://console.anthropic.com
export ANTHROPIC_API_KEY=your-key-here
python tools/ai_bug_reporter/ai_bug_reporter.py path/to/failure.log --version v3 --context "..."
```

### sql_analysis

SQLite-based analysis suite for QA test run data and real-world GitHub issue data.

- `setup_db.py` — creates and seeds the `test_runs` table with simulated QA data
  (auth and payment modules over 5 days)
- `queries.py` — aggregate queries: total failures by module, by date, failure rate %
- `window_functions.py` — demonstrates `ROW_NUMBER()` and `RANK()` partitioned by module
- `load_real_data.py` — loads real VSCode GitHub issues from `vscode_issues.json`
- `real_data_queries.py` — generates an issues health report:

```
=== VSCode Issues Health Report ===
Total issues: 200
Unlabeled issues: 42 (21.00%)
Labeled issues: 158 (79.00%)
=== Resolution time ===
Fastest issue: 0.1 hours
Slowest issue: 8736.5 hours
Average issue: 412.3 hours
=== The date in a week with the most issues created ===
Wednesday with 38 issues created
```

## Project structure

```
qa-toolkit/
├── evaluation/
│   ├── frameworks/                    # reusable templates
│   │   ├── system_overview_template.md
│   │   ├── evaluation_report_template.md
│   │   └── ai_evaluation_framework.md
│   └── projects/
│       └── fastapi-todo/              # full evaluation case study
│           ├── system_overview.md
│           ├── issues_found.md
│           ├── evaluation_summary.md
│           ├── docker_debug_log.md
│           ├── ai_evaluation.md
│           ├── ai_reports/            # raw AI outputs, graded
│           └── evaluations/
│               └── v1_initial_evaluation.md
├── tools/
│   ├── ai_bug_reporter/
│   │   └── ai_bug_reporter.py
│   ├── api_checker/
│   │   ├── api_checker.py
│   │   └── api_log_analyzer.py
│   ├── json_diff/
│   │   └── json_diff.py
│   ├── log_monitor/
│   │   ├── log_reader.py
│   │   ├── log_watcher.py
│   │   └── log_generator.py
│   └── sql_analysis/
│       ├── setup_db.py
│       ├── queries.py
│       ├── window_functions.py
│       ├── load_real_data.py
│       ├── real_data_queries.py
│       └── visualize.py
├── tests/
│   ├── toolkit/                       # unit tests — mocked, run in CI
│   │   ├── fixtures/
│   │   ├── test_api_checker.py
│   │   ├── test_json_diff.py
│   │   └── test_log_reader.py
│   └── probes/                        # evaluation probes — hit live target app
│       └── fastapi-todo/
│           ├── conftest.py
│           ├── test_create_todo.py
│           ├── test_get_todo_by_id.py
│           ├── test_get_todos.py
│           ├── test_update_todo.py
│           ├── test_delete_todo.py
│           ├── test_lifecycle.py
│           └── outputs/
│               └── test_log.txt
├── research/                          # deep-dives into open-source issues
│   └── requests-2086-iso-8859-1-fallback.md
├── runbooks/                          # incident response guides
│   ├── triage.md
│   ├── debug-4xx.md
│   ├── debug-5xx.md
│   ├── debug-json-mismatch.md
│   ├── debug-log-alert.md
│   └── debug-slow-api.md
├── .github/workflows/test.yml
├── .gitignore
├── requirements.txt
└── README.md
```

## How to run

```bash
# Static log analysis
cd tools/log_monitor && python log_reader.py

# Real-time log monitoring (open two terminals)
python log_generator.py             # terminal 1: generate live logs
python log_watcher.py live_app.log  # terminal 2: watch and alert

# JSON comparison
cd tools/json_diff && python json_diff.py

# API health check
cd tools/api_checker
python api_checker.py            # runs checks, writes api_health.log
python api_log_analyzer.py       # reads log, prints summary report

# AI bug report generation (requires Anthropic API key)
# Get a key at https://console.anthropic.com
export ANTHROPIC_API_KEY=your-key-here
cd tools/ai_bug_reporter
python ai_bug_reporter.py path/to/failure.log --version v3

# SQL analysis (simulated data)
cd tools/sql_analysis
python setup_db.py                       # create and seed database
python queries.py                        # aggregate queries
python window_functions.py              # window function queries

# SQL analysis (real VSCode GitHub data)
cd tools/sql_analysis
python load_real_data.py                 # load vscode_issues.json into DB
python real_data_queries.py              # generate issues health report
```

## Troubleshooting

When a tool surfaces an issue, use the runbooks to debug step by step:

| Tool output | Runbook |
|---|---|
| `api_checker` → ❌ status 5xx | [debug-5xx.md](runbooks/debug-5xx.md) |
| `api_checker` → ❌ status 4xx | [debug-4xx.md](runbooks/debug-4xx.md) |
| `api_checker` → ⚠️ slow response | [debug-slow-api.md](runbooks/debug-slow-api.md) |
| `log_watcher` → 🚨 ALERT | [debug-log-alert.md](runbooks/debug-log-alert.md) |
| `json_diff` → missing keys / diff values | [debug-json-mismatch.md](runbooks/debug-json-mismatch.md) |

Not sure which applies? Start at [triage.md](runbooks/triage.md).

## Testing

Two separate suites, because they test different things:

```bash
# Toolkit tests — mocked, no external dependencies, run in CI
pytest tests/toolkit -v

# Probe tests — hit a real running instance of the target app
# Start the target app first (e.g. uvicorn main:app --reload at localhost:8000)
pytest tests/probes/fastapi-todo -v
```

## Requirements

```bash
pip install -r requirements.txt
```

| Package | Used by |
|---|---|
| `requests` | `api_checker` — HTTP calls; `tests/probes` — hitting the target app |
| `pytest` | test suite |
| `responses` | `test_api_checker` — intercepts HTTP without a real server |
| `matplotlib` | `sql_analysis/visualize.py` |
| `anthropic` | `ai_bug_reporter` — Claude API calls |

All other modules (`sqlite3`, `collections`, `datetime`, `time`, `json`, `os`) are
part of the Python standard library.