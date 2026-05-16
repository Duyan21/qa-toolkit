# Debug: Slow API / Timeout

Use when `api_checker` reports ⚠️ (response time > 500ms) or a request receives no response.
Not sure this is your issue? → [triage.md](triage.md)

> Slow APIs and timeouts are rarely a code bug — they usually point to infrastructure, data volume, or an external dependency.

---

## Step 0 — Identify the type of problem

| Symptom                                    | Direction                           |
|--------------------------------------------|-------------------------------------|
| Response time > 500ms but a response arrives | Slow response → check performance |
| Connection timeout, no response at all     | Network issue or service is down    |
| Only one specific endpoint is slow         | Query or logic in that endpoint     |
| All endpoints across the service are slow  | Infrastructure or resource issue    |

---

## Step 1 — Measure and isolate

- [ ] What is the exact response time? (500ms? 2s? 10s?)
- [ ] Is only this endpoint slow, or multiple endpoints?
- [ ] Is it slow in all environments or just one?
- [ ] Is it consistently slow or only at certain times (e.g. peak hours)?

---

## Step 2 — Check layer by layer

### Network
- [ ] Is ping / traceroute to the host normal?
- [ ] Is DNS resolution slow?

### Application
- [ ] Does this endpoint perform heavy computation? (large loops, many transforms)
- [ ] Does it make external API calls internally?

### Database
- [ ] Is the query using an index?
- [ ] Is the data volume unusually large? (full table scan?)
- [ ] Is the connection pool exhausted?

### Infrastructure
- [ ] Are CPU and memory on the server within normal range?
- [ ] Was there a recent traffic spike?

---

## Step 3 — Reproduce and re-measure

- [ ] Call the endpoint multiple times — is response time stable or fluctuating?
- [ ] Try with a smaller payload — does time improve?
- [ ] Try during low-traffic hours — still slow?

---

## Step 4 — Escalate if needed

⏱ If the slow layer cannot be identified after **30 minutes** → escalate
Prepare: response time log from `api_checker`, environment, and time of occurrence

→ See escalation contacts at [triage.md](triage.md)

---

## Step 5 — Verify the fix

- [ ] Re-run `api_checker` → response time is below threshold?
- [ ] Measure at least 3–5 consecutive times to confirm stability

```
Root cause   : 
Fix applied  : 
Follow-up    : [ ] Yes  [ ] No  →
```
