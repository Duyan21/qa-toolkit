# AI Evaluation Framework

> **Purpose:** Generic framework for evaluating AI output quality. Apply to any AI tool, any project, any domain.
> **How to use:** Copy into project's `ai_evaluation.md`, fill sections relevant to your evaluation.
> **Living document:** Update framework criteria as you learn from each evaluation.

---

## 1. Evaluation Scope

**What AI tool/feature:** _[name and one-line description]_
**What it takes as input:** _[type of data: test logs, documents, user queries...]_
**What it produces:** _[type of output: bug reports, summaries, classifications...]_
**Why it exists:** _[what problem does this AI feature solve]_
**What "good output" looks like:** _[define before evaluating — if you can't define good, you can't judge]_

---

## 2. Evaluation Methodology

### 2.1 Approach

_Describe how you evaluated. Pick applicable methods:_

- [ ] **Prompt iteration** — tested N versions, measured impact of each change
- [ ] **Golden dataset comparison** — compared AI output against known-correct answers
- [ ] **Expert judgment** — compared AI output against what a domain expert would produce
- [ ] **A/B comparison** — compared outputs from different models/prompts on same input
- [ ] **Adversarial probing** — deliberately fed edge cases, ambiguous input, misleading data

### 2.2 Input Selection

_How you chose what to feed the AI. Important because input selection biases results._

| Input type | Why selected | Count |
|-----------|-------------|-------|
| _[e.g. typical test failure]_ | _[baseline — does it work on normal cases?]_ | _[N]_ |
| _[e.g. complex cascade failure]_ | _[stress test — can it handle depth?]_ | _[N]_ |
| _[e.g. ambiguous/misleading input]_ | _[adversarial — when does it break?]_ | _[N]_ |

**Total cases evaluated:** _[minimum 15 for meaningful patterns]_

### 2.3 Context Iteration (if applicable)

_Document what context was provided to the AI and the impact of each layer._

| Version | Context provided | Purpose |
|---------|-----------------|---------|
| v1 | None (bare minimum) | Establish baseline |
| v2 | Output structure requested | Measure structure impact |
| v3 | Domain/tech context | Measure domain knowledge impact |
| v4 | System documentation | Measure deep context impact |
| v5 | System health/status | Measure operational context impact |

---

## 3. Quality Criteria

_These criteria apply to any AI output. Score each case against all applicable criteria._

### 3.1 Core Criteria (always evaluate)

| Criteria | Question | How to check |
|----------|----------|-------------|
| **Factual correctness** | Is the output true? | Compare against known facts, source data, expert knowledge |
| **Completeness** | Is important information missing? | Check: would someone acting on this output miss something critical? |
| **Relevance** | Does it answer what was asked? | Check: is there off-topic content, or missing the point? |
| **Actionability** | Can someone act on this output? | Check: does the reader know what to do next? |

### 3.2 Context-Dependent Criteria (evaluate when applicable)

| Criteria | Question | When to apply |
|----------|----------|--------------|
| **Consistency** | Same input → same quality output? | When output is non-deterministic |
| **Severity accuracy** | Is risk/priority correctly assessed? | When output includes severity/priority |
| **Root cause depth** | Surface symptom or actual root cause? | When output includes analysis |
| **Cascade awareness** | Does it connect related issues? | When multiple failures may share root cause |
| **Hallucination** | Is it making things up? | Always, but especially with technical details |
| **Harmful potential** | If wrong, what's the consequence? | When output drives decisions |

### 3.3 Scoring Guide

```
✅ CORRECT    — Accurate, complete, actionable
⚠️ PARTIAL    — Partially correct but missing depth, context, or nuance
❌ INCORRECT  — Factually wrong, misleading, or would lead to wrong action
🤖 HALLUCINATED — Confident statement with no basis in input data
```

---

## 4. Results Table

_One row per evaluated case. Minimum 15 cases for meaningful evaluation._

| # | Input description | AI Output summary | Correct? | Criteria failed | Notes |
|---|-------------------|-------------------|----------|----------------|-------|
| 1 | _[what you fed it]_ | _[what it produced]_ | ✅/⚠️/❌/🤖 | _[which criteria]_ | _[why]_ |
| 2 | | | | | |
| ... | | | | | |

**Summary:**
- Total cases: _[N]_
- ✅ Correct: _[N]_ (_[%]_)
- ⚠️ Partial: _[N]_ (_[%]_)
- ❌ Incorrect: _[N]_ (_[%]_)
- 🤖 Hallucinated: _[N]_ (_[%]_)

---

## 5. Prompt Iteration Log

_Document each prompt version and its impact on output quality._

| Version | What changed | Impact on output | Quality delta |
|---------|-------------|------------------|--------------|
| v1 | _[baseline — no context]_ | _[observations]_ | baseline |
| v2 | _[added X]_ | _[what improved/degraded]_ | _[+/-]_ |
| v3 | _[added Y]_ | _[what improved/degraded]_ | _[+/-]_ |

**Key finding:** _[which change had the biggest positive impact and why]_

---

## 6. Failure Modes Identified

_Patterns of when and how AI output fails. Most valuable section for future reference._

### 6.1 Failure Mode Catalog

| # | Mode | Description | Frequency | Example |
|---|------|------------|-----------|---------|
| FM-1 | _[name]_ | _[what happens]_ | _[how often in N cases]_ | _[specific case #]_ |
| FM-2 | | | | |

### 6.2 Common Failure Patterns

_Group individual failures into patterns:_

- **[Pattern name]:** _[description — when does this pattern appear, what triggers it]_
- **[Pattern name]:** _[description]_

---

## 7. When NOT to Trust This Output

_Most important section for evaluator. Specific conditions where AI output should not be used without human verification._

### 7.1 High-Risk Conditions

_AI output should NOT be trusted when:_

- _[condition 1 — e.g. "input contains multiple related failures — AI treats as independent"]_
- _[condition 2 — e.g. "output includes severity assessment without domain context"]_
- _[condition 3]_

### 7.2 Required Human Verification

_Even when output looks correct, always verify:_

- _[what to verify — e.g. "root cause analysis — AI often describes symptoms, not causes"]_
- _[what to verify]_

### 7.3 Acceptable Use Cases

_AI output CAN be trusted for:_

- _[case — e.g. "initial triage of simple, single-cause failures"]_
- _[case — e.g. "generating structured format from unstructured error logs"]_

---

## 8. Recommendations

### 8.1 For This Tool

_Specific improvements for the AI tool evaluated:_

- _[recommendation]_

### 8.2 For AI Integration Generally

_Lessons that apply to any AI integration:_

- _[lesson]_

---

## 9. Evaluation Metadata

| Item | Value |
|------|-------|
| Evaluator | _[name]_ |
| Date | _[date]_ |
| Model used | _[model name + version]_ |
| Total cases | _[N]_ |
| Total prompt versions | _[N]_ |
| Time spent | _[hours]_ |
| Cost | _[estimated API cost]_ |