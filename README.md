# QA Toolkit

A collection of CLI scripts that automate common QA and engineering workflows —
turning raw logs, API responses, JSON data, and real-world datasets into actionable insights.

## Tools

### log_reader
Parses a static application log file and summarizes ERROR lines by type and frequency.
Useful for post-deployment checks and incident investigation.

```
Total error occurrences: 5
 - Database connection failed: timeout (x3)
 - Auth service unreachable (x2)
```

### log_watcher
Monitors a live log file in real time (tail-mode). Fires an alert when error frequency
exceeds a configurable threshold within a sliding time window, prints periodic summaries,
and generates a session report on exit.

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
Compares two JSON files and reports missing keys and value differences.
Useful for verifying API contract consistency across environments (e.g. staging vs production).

```
Missing keys in production: 1
 - last_login

Different values: 1
 - role: staging='admin' vs production='viewer'

Identical: 3
 status, user_id, email
```

### api_checker + api_log_analyzer
Checks API health across multiple endpoints — status code, response time, and field count.
Writes results to a log file, then generates a summary report.

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

### sql_analysis
SQLite-based analysis suite for QA test run data and real-world GitHub issue data.

**setup_db.py** — creates and seeds the `test_runs` table with simulated QA data
(auth and payment modules over 5 days).

**queries.py** — runs aggregate SQL queries against `test_runs`:
- Total failed tests by module
- Failed tests by date and module
- Failure rate (%) by module and date

**window_functions.py** — demonstrates advanced SQL window functions on `test_runs`:
- `ROW_NUMBER() OVER (PARTITION BY module ORDER BY failure_rate DESC)` — unique rank per module
- `RANK() OVER (PARTITION BY module ORDER BY failure_rate DESC)` — rank with ties

**load_real_data.py** — loads real VSCode GitHub issues from `vscode_issues.json` into
`github_issues` and `issue_labels` tables.

**real_data_queries.py** — generates a health report from real issue data:

```
=== VSCode Issues Health Report ===
Total issues: 200
Unlabeled issues: 42 (21.00%)
Labeled issues: 158 (79.00%)
=== Labeled breakdown ===
bug: 63 (39.87%)
...
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
├── tools/
│   ├── log_monitor/
│   │   ├── log_reader.py        # static log parser
│   │   ├── log_watcher.py       # real-time log monitor with alerting
│   │   ├── log_generator.py     # simulates a live app writing log entries
│   │   └── sample.log
│   ├── json_diff/
│   │   ├── json_diff.py
│   │   ├── staging.json
│   │   └── production.json
│   ├── api_checker/
│   │   ├── api_checker.py
│   │   ├── api_log_analyzer.py
│   │   └── api_health.log
│   └── sql_analysis/
│       ├── setup_db.py          # seed simulated test run data
│       ├── queries.py           # aggregate queries on test_runs
│       ├── window_functions.py  # ROW_NUMBER / RANK window queries
│       ├── load_real_data.py    # load real VSCode GitHub issues
│       ├── real_data_queries.py # health report on real issue data
│       └── vscode_issues.json
├── runbooks/                    # incident response guides
└── docs/                        # deep-dives and issue analysis
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

# SQL analysis (simulated data)
cd tools/sql_analysis
python setup_db.py               # create and seed database
python queries.py                # aggregate queries
python window_functions.py       # window function queries

# SQL analysis (real VSCode GitHub data)
python load_real_data.py         # load vscode_issues.json into DB
python real_data_queries.py      # generate issues health report
```

## Troubleshooting

When a tool surfaces an issue, use the runbooks to debug step by step:

| Tool output                              | Runbook                                  |
|------------------------------------------|------------------------------------------|
| `api_checker` → ❌ status 5xx            | [runbooks/debug-5xx.md](runbooks/debug-5xx.md) |
| `api_checker` → ❌ status 4xx            | [runbooks/debug-4xx.md](runbooks/debug-4xx.md) |
| `api_checker` → ⚠️ slow response         | [runbooks/debug-slow-api.md](runbooks/debug-slow-api.md) |
| `log_watcher` → 🚨 ALERT                 | [runbooks/debug-log-alert.md](runbooks/debug-log-alert.md) |
| `json_diff` → missing keys / diff values | [runbooks/debug-json-mismatch.md](runbooks/debug-json-mismatch.md) |

Not sure which applies? Start at [runbooks/triage.md](runbooks/triage.md).

## Requirements

```bash
pip install requests
```

All other modules (`sqlite3`, `collections`, `datetime`, `time`, `json`) are part of the Python standard library.

## Documentation

- [Runbooks](runbooks/triage.md) — incident response guides
- [Issue Analysis](docs/issue-analysis/) — deep-dives into open-source bugs
