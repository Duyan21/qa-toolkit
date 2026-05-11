# QA Toolkit

A collection of scripts to automate common QA workflows — log analysis, data validation, API health checks.

## Tools
- log_reader.py — parse and summarize ERROR lines from log files
- json_diff.py - compare JSON files, report missing keys and value differences
- api_checker.py - call API, print status + response summary
## How to run

- log_reader
```bash
cd qa-toolkit/log_reader
python log_reader.py
```

> Make sure `sample.log` is in the same directory.

- json_diff
```bash
cd qa-toolkit/json_diff
python json_diff.py
```

- api_checker
```bash
cd qa-toolkit/api_checker
python api_checker.py
```
