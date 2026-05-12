# QA Toolkit

A collection of CLI scripts that automate common QA and engineering workflows — 
turning raw logs, API responses, and JSON data into actionable insights.

## Tools

### log_reader
Parses application log files and summarizes ERROR lines by type and frequency.
Useful for post-deployment checks and incident investigation.

**Output:**

Total error occurrences: 5

- Database connection failed: timeout (x3)
- Auth service unreachable (x2)

### json_diff
Compares two JSON files and reports missing keys and value differences.
Useful for verifying API contract consistency across environments (e.g. staging vs production).

**Output:**

Missing keys in production: 1

- last_login

Different values: 1

- role: staging='admin' vs production='viewer'

- Identical: 3

status, user_id, email

### api_checker + api_log_analyzer
Checks API health across multiple endpoints — status code, response time, and field count.
Writes results to a log file, then generates a summary report.

**Output:**

Total API checks: 3
Passed ✅: 0
Slow ⚠️: 3  (threshold: 500ms)
Failed ❌: 0
=== Slow APIs ⚠️ ===
 - https://api.github.com/users/torvalds (Response time: 922 ms)
 - https://api.github.com/repos/facebook/react (Response time: 955 ms)
 - https://jsonplaceholder.typicode.com/users/1 (Response time: 1348 ms)

## How to run

```bash
# Log analysis
cd log_reader && python log_reader.py

# JSON comparison
cd json_diff && python json_diff.py

# API health check
cd api_checker
python api_checker.py        # runs checks, writes api_health.log
python api_log_analyzer.py   # reads log, prints summary report
```

## Requirements
```bash
pip install requests
```