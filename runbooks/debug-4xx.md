# Debug: API 4xx Errors

Use when `api_checker` reports ❌ with status 400, 401, 403, 404, or 422.
Not sure this is your issue? → [triage.md](triage.md)

> 4xx = client-side error. Inspect the request first — no need to dig into server logs yet.

---

## Step 0 — Identify the status code

| Code | Meaning                  | First debug direction                    |
|------|--------------------------|------------------------------------------|
| 400  | Bad Request              | Check request body format / schema       |
| 401  | Unauthorized             | Check token or API key                   |
| 403  | Forbidden                | Check permission or role                 |
| 404  | Not Found                | Check URL and whether the resource exists |
| 422  | Unprocessable Entity     | Check API validation rules               |

---

## Step 1 — Inspect the request

- [ ] Is the URL correct? (typo, trailing slash, version `/v1` vs `/v2`)
- [ ] Is the HTTP method correct? (GET / POST / PUT / PATCH / DELETE)
- [ ] Are all required headers present? (`Content-Type`, `Authorization`, `Accept`)
- [ ] Is the request body valid? (valid JSON, all required fields included)

---

## Step 2 — Drill down by status code

### 401 Unauthorized
- [ ] Is the token still valid (not expired)?
- [ ] Is the token sent correctly? (`Bearer` prefix, correct header name)
- [ ] Is the API key for the right environment? (staging key used in production?)

### 403 Forbidden
- [ ] Does the user or service account have the correct role or permission?
- [ ] Is the resource restricted by IP, org, or plan?

### 404 Not Found
- [ ] Does the resource exist? (deleted, not yet created, or wrong ID?)
- [ ] Is the URL path correct? Compare against API docs

### 422 Unprocessable Entity
- [ ] Read the response body carefully — usually contains an `errors` field with details
- [ ] Compare the request body against the schema the API expects

---

## Step 3 — Reproduce and isolate

- [ ] Try calling directly with `curl` or Postman to rule out a code-level issue
- [ ] Does the error occur for all users or only some? (only some → permission issue)
- [ ] Does the error occur in all environments or only production? (only prod → config difference)

---

## Step 4 — Escalate if needed

⏱ If the root cause is still unclear after **30 minutes** → escalate
Prepare: raw request + raw response to share immediately

→ See escalation contacts at [triage.md](triage.md)

---

## Step 5 — Verify the fix

- [ ] Reproduce again → response is now correct?
- [ ] Test with different users or roles if it was a permission issue
- [ ] Does this runbook need updating based on what you learned?

```
Root cause   : 
Fix applied  : 
Follow-up    : [ ] Yes  [ ] No  →
```
