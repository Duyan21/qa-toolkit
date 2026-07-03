# Evaluation Report — [Version] [Trigger]

> **System:** _[system name]_
> **Evaluated by:** _[name]_
> **Date:** _[date]_
> **Status:** IN PROGRESS / FROZEN — do not edit after completion

---

## 1. Evaluation Scope

**What system:** _[one-line description + tech stack]_

**What version:** _[v1 initial / v2 post-feature / v3 post-incident]_

**What triggered this evaluation:**
_[Why this evaluation happened — initial review, new feature, incident, periodic review, compliance requirement]_

**What was in scope:**

| Area | Status |
|------|--------|
| System overview + architecture | ✅ / ⏳ / ❌ N/A |
| Documentation quality | ✅ / ⏳ / ❌ N/A |
| API / feature functionality | ✅ / ⏳ / ❌ N/A |
| Cross-feature lifecycle | ✅ / ⏳ / ❌ N/A |
| Docker / deployment readiness | ✅ / ⏳ / ❌ N/A |
| AI integration quality | ✅ / ⏳ / ❌ N/A |
| Security | ✅ / ⏳ / ❌ N/A |
| Performance | ✅ / ⏳ / ❌ N/A |

**What was NOT in scope:** _[explicitly state what you did not evaluate and why]_

---

## 2. Methodology

_Describe how you evaluated — what steps, in what order, with what tools._

| Step | Method | Purpose |
|------|--------|---------|
| 1 | _[e.g. Document review]_ | _[e.g. Map architecture, assess doc quality]_ |
| 2 | _[e.g. Feature decomposition]_ | _[e.g. List all endpoints, verify against code]_ |
| 3 | _[e.g. E2E trace]_ | _[e.g. Trace one request through all layers]_ |
| 4 | _[e.g. Probe tests]_ | _[e.g. Verify assumptions with targeted tests]_ |
| 5 | _[e.g. Docker-readiness assessment]_ | _[e.g. Containerize, document breakage]_ |
| 6 | _[e.g. AI evaluation]_ | _[e.g. Evaluate AI output quality]_ |

---

## 3. Risk Areas (ranked by severity)

_Most critical findings. Ranked P0 → P3. Each risk must have evidence._

### RISK-001: _[title]_

**Evidence:** _[what you observed — specific, reproducible]_
**Severity:** _[P0/P1/P2/P3]_ _[tutorial context vs production context if different]_
**Business impact:** _[who is affected, what happens if not fixed]_
**Related issue:** _[ISS-XXX in issues_found.md]_
**Status:** OPEN / RESOLVED

---

### RISK-002: _[title]_

_[same format]_

---

_(add more as needed)_

---

## 4. Probe Test Results

### 4a. Summary

| Metric | Value |
|--------|-------|
| Total probes | _[N]_ |
| Pass | _[N]_ |
| Fail | _[N]_ |
| Gaps found | _[N]_ |

### 4b. Results by Feature

_Group probes by feature area. Each fail links to a finding in Section 3._

#### Feature 1: _[name]_

| ID | Probe | Expected | Actual | Result |
|----|-------|----------|--------|--------|
| _[ID]_ | _[what you tested]_ | _[expected]_ | _[actual]_ | ✅ / ❌ / GAP |

#### Feature 2: _[name]_

_[same format]_

#### Cross-Feature / Lifecycle

_[same format]_

### 4c. Known Gaps

_Findings that aren't bugs — they're missing constraints or features._

| Gap | Affected Features | Risk |
|-----|------------------|------|
| _[description]_ | _[which features]_ | _[what could go wrong]_ |

---

## 5. Additional Assessments (if applicable)

### 5a. Docker-Readiness (if evaluated)

| Item | Status | Finding |
|------|--------|---------|
| Dockerfile exists | ✅ / ❌ | _[notes]_ |
| .dockerignore | ✅ / ❌ | _[notes]_ |
| Dependencies pinned | ✅ / ❌ | _[notes]_ |
| Env vars externalized | ✅ / ❌ | _[notes]_ |
| Config separable | ✅ / ❌ | _[notes]_ |
| Health check endpoint | ✅ / ❌ | _[notes]_ |
| Secrets exposure | ✅ / ❌ | _[notes]_ |

_Debug scenarios documented in docker_debug_log.md._

### 5b. AI Output Quality (if evaluated)

_Summary from ai_evaluation.md:_

| Metric | Value |
|--------|-------|
| Total cases evaluated | _[N]_ |
| Correct | _[N]_ (_[%]_) |
| Partial | _[N]_ (_[%]_) |
| Incorrect | _[N]_ (_[%]_) |
| Top failure mode | _[description]_ |
| Context with biggest impact | _[which version/context]_ |

_Full results in ai_evaluation.md. Raw AI outputs in ai_reports/._

---

## 6. Assumptions Log

_Assumptions formed during evaluation. Track status as evidence confirms or rejects them._

| # | Assumption | Basis | Status |
|---|-----------|-------|--------|
| A1 | _[what you assumed]_ | _[why — README, code, inference]_ | CONFIRMED / REJECTED / UNCONFIRMED |
| A2 | | | |

---

## 7. Open Questions

_Things still unknown after evaluation. Each must explain why it matters._

| # | Question | Why it matters |
|---|---------|---------------|
| Q1 | _[question]_ | _[impact of not knowing]_ |
| Q2 | | |

---

## 8. Recommendation

**Acceptable as:** _[what context this system is safe for]_

**Not ready for:** _[what context this system is NOT safe for, with reasons]_

**Priority fixes:**
1. _[P1 fixes first — what and why]_
2. _[P2 fixes next]_
3. _[P2 fixes]_

**Overall quality signal:**
_[2-3 sentences summarizing: how many findings, what severity distribution, where risks concentrate, is architecture change needed or just config/validation fixes]_

**Pending:** _[anything not yet evaluated that should be in next version]_

---

## Evaluation Metadata

| Item | Value |
|------|-------|
| Evaluator | _[name]_ |
| Date range | _[start — end]_ |
| Version | _[v1/v2/v3]_ |
| Trigger | _[why this evaluation]_ |
| Tools used | _[probe tests, AI tool, Docker, etc.]_ |
| Documents produced | _[list all files in this evaluation]_ |
| Next evaluation trigger | _[what should trigger v2]_ |