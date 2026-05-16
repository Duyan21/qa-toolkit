# Debug: API 5xx Errors

Use when `api_checker` reports ❌ with status 500, 502, 503, or 504.
Not sure this is your issue? → [triage.md](triage.md)

---

## Step 0 — Reproduce (do this before anything else)

- [ ] Can you reproduce the error?
- [ ] Reproduction rate: 100% / intermittent / only on a specific endpoint?
- [ ] If not reproducible → **stop**, collect more logs before continuing

---

## Step 1 — Read the response

- [ ] What is the exact status code? (500 / 502 / 503 / 504)
- [ ] What does the response body say? (error message, stack trace if present)
- [ ] Is the error message specific enough, or is it a generic message?

> **Quick reference:**
> - `500` Internal Server Error → bug in the service's own code
> - `502` Bad Gateway → upstream service is not responding
> - `503` Service Unavailable → service is overloaded or down
> - `504` Gateway Timeout → upstream service is too slow to respond

---

## Step 2 — Collect information

- [ ] Full request details: URL, method, headers, body
- [ ] Timestamp and timezone of the failing request
- [ ] Environment: local / staging / production?
- [ ] Frequency: always failing or intermittent?
- [ ] Any recent deploy or config change?

---

## Step 3 — Check logs

- [ ] Server logs around the time the error occurred
- [ ] Any pattern — has a similar error happened before?
- [ ] Use `log_watcher` or `log_reader` to parse if log volume is high

> **For systems with a BFF layer:**
> - HTTP 200 does not mean success
> - Always check the response body — it may contain a `status`, `code`, or `error` field
> - Trace the request through each layer: FE → BFF → Service

---

## Step 4 — Escalate if needed

⏱ If the root cause is still unclear after **30 minutes** → escalate immediately

- [ ] Can you summarize: "Error X occurs at Y, frequency Z, tried A and B"?
- [ ] Identified the team that owns the service?
- [ ] → See escalation contacts at [triage.md](triage.md)

---

## Step 5 — Verify the fix

- [ ] Reproduce the original scenario → error no longer occurs?
- [ ] Check related endpoints — no regressions?
- [ ] Is there a test case covering this? If not → add one
- [ ] Does this runbook need updating based on what you learned?

**Record after fixing:**

```
Root cause   : 
Fix applied  : 
Follow-up    : [ ] Yes  [ ] No  →
```
