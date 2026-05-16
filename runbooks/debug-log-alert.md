# Debug: Log Watcher Alert

Use when `log_watcher` fires 🚨 ALERT — error frequency has exceeded the threshold within the sliding window.
Not sure this is your issue? → [triage.md](triage.md)

---

## Read the alert output first

When `log_watcher` fires, it prints:

```
🚨 ALERT: 5 errors in 60 seconds
   From: 10:00:05 → 10:00:58
```

Collect immediately:
- [ ] How many errors occurred in what time window?
- [ ] What is the error type? (check the summary printed below the alert)
- [ ] When did it start — did anything happen just before? (deploy, cron job, traffic spike)

---

## Step 1 — Read the session summary

`log_watcher` prints a periodic summary and a session report on exit:

```
Total errors: 7
  - Database connection failed: timeout (x4)
  - Auth service unreachable (x3)
```

- [ ] Which error type has the highest count?
- [ ] Is one error type spiking, or multiple types at the same time?
  - One type spiking → issue is in a specific service
  - Multiple types simultaneously → likely an infrastructure issue

---

## Step 2 — Assess severity

| Situation                              | Severity | Action              |
|----------------------------------------|----------|---------------------|
| Error rate is rising but now declining | Low      | Keep monitoring     |
| Error rate is stable at a high level   | Medium   | Debug now           |
| Error rate is continuously increasing  | High     | Escalate now        |
| Entire service is not responding       | Critical | Escalate + page oncall |

---

## Step 3 — Route to the right runbook

Based on the error messages in the log:

- API / HTTP status errors → [debug-5xx.md](debug-5xx.md) or [debug-4xx.md](debug-4xx.md)
- Response time / timeout errors → [debug-slow-api.md](debug-slow-api.md)
- Database / connection errors → inspect the database layer directly
- Auth / token errors → [debug-4xx.md](debug-4xx.md) → section 401

---

## Step 4 — Escalate if needed

⏱ If severity is **High or Critical** → do not wait 30 minutes, escalate immediately

Prepare when escalating:
- Copy the full alert output + summary from `log_watcher`
- Start time and current error frequency

→ See escalation contacts at [triage.md](triage.md)

---

## Step 5 — Verify stability

- [ ] Has the error rate returned to zero or normal baseline?
- [ ] Does `log_watcher` remain quiet for the next 10 minutes?
- [ ] Does this runbook need updating based on what you learned?

```
Root cause   : 
Fix applied  : 
Follow-up    : [ ] Yes  [ ] No  →
```
