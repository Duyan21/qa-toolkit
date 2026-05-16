# Debug: JSON Mismatch (staging vs production)

Use when `json_diff` reports missing keys or different values between two environments.
Not sure this is your issue? → [triage.md](triage.md)

> JSON mismatches between staging and production are rarely a code bug —
> they usually point to config drift, an incomplete deploy, or a migration that hasn't run.

---

## Read the json_diff output first

```
Missing keys in production: 1
 - last_login

Different values: 1
 - role: staging='admin' vs production='viewer'

Identical: 3
 status, user_id, email
```

Collect immediately:
- [ ] Which keys are missing? Which fields have different values?
- [ ] Missing key vs different value — these have different root causes

---

## Step 1 — Classify the problem

| Symptom                                  | Likely cause                                    |
|------------------------------------------|-------------------------------------------------|
| Key exists in staging, missing in prod   | Incomplete deploy or migration not yet run      |
| Key exists in prod, missing in staging   | Staging is running an older version             |
| Same key but different values            | Environment-specific config difference          |
| Multiple keys missing at once            | Schema change not applied to one environment    |

---

## Step 2 — Identify the source

- [ ] Where does the mismatched field come from? (API response, config file, database, feature flag)
- [ ] Are both environments running the same version of the code?
- [ ] Was there a recent deploy to one environment but not the other?
- [ ] Is there a migration or seed script that still needs to run in production?

---

## Step 3 — Verify manually

- [ ] Call the endpoint directly on both environments and compare responses
- [ ] Check config and environment variables across both environments
- [ ] If it is a database field: check whether the schema matches on both sides

---

## Step 4 — Escalate if needed

⏱ If the root cause is still unclear after **30 minutes** → escalate

Prepare when escalating:
- Full output from `json_diff`
- Code version currently running in each environment
- When the mismatch first appeared (if known)

→ See escalation contacts at [triage.md](triage.md)

---

## Step 5 — Verify the fix

- [ ] Re-run `json_diff` after the fix → no more mismatches?
- [ ] Run in both directions: staging vs prod and prod vs staging
- [ ] Does this runbook need updating based on what you learned?

```
Root cause   : 
Fix applied  : 
Follow-up    : [ ] Yes  [ ] No  →
```
