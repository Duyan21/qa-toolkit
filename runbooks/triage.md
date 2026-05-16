# Triage — Start Here

Identify the symptom, open the right runbook. Do not read everything at once.

---

## Step 0 — What is the severity? (decide this first)

| Situation                                              | Severity    | Immediate action                  |
|--------------------------------------------------------|-------------|-----------------------------------|
| Entire service is down, users cannot access            | P1 Critical | Page oncall immediately, no delay |
| A core feature is broken 100%, no workaround available | P2 High     | Fix within 1 hour, notify team    |
| Intermittent errors or a temporary workaround exists   | P3 Medium   | Fix during business hours         |
| A single endpoint is slow, no impact on user flow      | P4 Low      | File a ticket, handle normally    |

> **Unsure about severity?** Default to the higher level and escalate.
> A false escalation can be corrected — a missed P1 cannot.

---

## What is my symptom?

| Symptom                                              | Runbook                                              |
|------------------------------------------------------|------------------------------------------------------|
| API returns `5xx` (500, 502, 503...)                 | [debug-5xx.md](debug-5xx.md)                         |
| API returns `4xx` (401, 403, 404, 422...)            | [debug-4xx.md](debug-4xx.md)                         |
| API returns `200` but response time > 500ms          | [debug-slow-api.md](debug-slow-api.md)               |
| `log_watcher` fires 🚨 ALERT                         | [debug-log-alert.md](debug-log-alert.md)             |
| `json_diff` detects mismatch between staging and prod | [debug-json-mismatch.md](debug-json-mismatch.md)    |

---

## Not sure what the symptom is?

Answer these 3 questions in order:

1. **Which tool detected the issue?**
   - `api_checker` → see the "API returns..." rows above
   - `log_watcher` → [debug-log-alert.md](debug-log-alert.md)
   - `json_diff` → [debug-json-mismatch.md](debug-json-mismatch.md)
   - Reported by a user → ask first: what is the status code?

2. **Where is the error occurring?**
   - Local only → likely a config or env issue
   - Staging / Production → escalate faster

3. **How frequent is it?**
   - 100% reproducible → debug immediately
   - Intermittent → collect logs first, reproduce later

---

## Time-box

> If the root cause is still unclear after **30 minutes** → escalate.
> Escalating is not a failure — it is the correct process.

---

## Escalation

- Slack: `#incident` or `#backend-oncall` _(update with your team's channel)_
- Ticket: create an issue using the [bug-report] template
- On-call: see rotation list at [rotation link] _(update with your team's link)_

---

## Improving a runbook

If you found a gap or inaccuracy in a runbook during an incident, file a ticket titled:

```
Runbook uplift: <filename>
```

Link it to the post-mortem or incident ticket so the context is preserved.
