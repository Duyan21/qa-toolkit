## 1. Evaluation Scope

**What AI tool/feature:** Bug Report Generation
**What it takes as input:** Test log, Documents (System overview, Evaluation summary, Issues Found)
**What it produces:** Bug report
**Why it exists:** It would help to generate bug report with effective structure and content so that any role who need this information can trust to use
**What "good output" looks like:** Follow a clear defined structure with detailed and correct answer

---

## 2. Evaluation Methodology

### 2.1 Approach


- **Prompt iteration** — tested 6 versions, later versions are more detailed and come with clearer instructions
- **Golden dataset comparison** — compared AI output against known-correct answers
- **Expert judgment** — compared AI output against what a domain expert would produce
- **A/B comparison** — compared outputs from different models/prompts on same input

### 2.2 Input Selection

_How you chose what to feed the AI. Important because input selection biases results._

| Input type | Why selected | Count |
|-----------|-------------|-------|
| Test failure log (8 failing tests, single run) | Baseline — does it work on the raw signal an engineer would actually paste in? | 1 log, reused across all 6 versions |
| Same log + increasing layers of documentation | Stress test — does more context fix root cause / cascade blindness, or only formatting? | 6 versions (V1–V6) |
| Cascade failure disguised as 8 independent failures | Adversarial — the log looks like 8 bugs but is actually 1 (ISS-004 corrupting a DB record, breaking every subsequent GET). Tests whether AI can see past surface symptoms. | 1 (embedded in the log used for all versions) |

**Total cases evaluated:** 6 (one per prompt version, same input).
Note: standard minimum is 15 cases across varied inputs. 
This evaluation uses a single complex input (8-failure cascade) 
across 6 context levels to isolate the impact of context, 
not input variety. A broader evaluation across different 
failure types would be a logical next step.

### 2.3 Context Iteration (if applicable)

_Document what context was provided to the AI and the impact of each layer._

| Version | Context provided | Purpose |
|---------|-----------------|---------|
| v1 | Test failure log only (bare minimum) | Establish baseline |
| v2 | + Output structure requested (sections: title, severity, expected/actual, tests) | Measure structure impact |
| v3 | + Tech context ("FastAPI CRUD app, SQLAlchemy, SQLite, Pydantic v2") + P0–P3 severity guide | Measure domain knowledge impact |
| v4 | + `system_overview.md` (architecture, code paths, user journey) | Measure deep context impact |
| v5 | + `evaluation_summary.md` (active risks, resolved issues, trend) | Measure operational/health context impact |
| v6 | + `issues_found.md` (full issue evidence, impact, fix recommendations, including ISS-004 in full) | Measure impact of giving AI the answer directly |

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

_One row per evaluated case (prompt version). Same underlying test failure log used in all 6 rows; only context provided to the AI changes._

| # | Input description | AI Output summary | Correct? | Criteria failed | Notes |
|---|-------------------|-------------------|----------|----------------|-------|
| 1 | V1 — test failure log only | 3 categories, 8 separate bugs, generic root causes | ⚠️ | Completeness, Root cause depth, Cascade awareness | Baseline. Shallow, not factually wrong — no severity possible (N/A), no structure. |
| 2 | V2 — + output structure requested | Requested sections present (title, severity, expected/actual, tests); root cause still guessed | ⚠️ | Root cause depth, Cascade awareness, Context usage | Format improved; content quality unchanged. |
| 3 | V3 — + tech context + P0–P3 severity guide | Sections complete, severity now justified (P1, "breaks CRUD operation") | ⚠️ | Root cause depth, Cascade awareness | Severity judgment became reliable for the first time. |
| 4 | V4 — + system_overview.md | Traced to `routers/todo.py`, identified serialization as involved; code-specific fix suggestions | ⚠️ | Root cause depth, Cascade awareness | Near-miss: raised "response serialization failure through TodoOut" then dismissed it with flawed logic (FM-4). |
| 5 | V5 — + evaluation_summary.md | Cross-referenced ISS-006, ISS-007, ISS-002; noted alignment with known risk landscape | ⚠️ | Root cause depth, Cascade awareness | Did not connect ISS-004 despite it appearing in the summary as the top active risk. |
| 6 | V6 — + issues_found.md (full ISS-004 detail) | Marginal improvement in cross-referencing only | ⚠️ | Root cause depth, Cascade awareness | Root cause of the cascade was present verbatim in the input and still not connected to the 8 failures. |

**Summary:**
- Total cases: 6
- ✅ Correct: 0 (0%)
- ⚠️ Partial: 6 (100%)
- ❌ Incorrect: 0 (0%)
- 🤖 Hallucinated: 0 (0%)

**Cross-cutting result:** Across all 6 versions, Factual correctness stayed ⚠️ and Cascade awareness stayed ❌ — no amount of added context moved either criterion. See [Section 6](#6-failure-modes-identified) for why.

---

## 5. Prompt Iteration Log

_Document each prompt version and its impact on output quality._

### 5.1 Scoring Table

| Criteria            | V1  | V2  | V3  | V4  | V5  | V6  |
|---------------------|-----|-----|-----|-----|-----|-----|
| Factual correctness | ⚠️  | ⚠️  | ⚠️  | ⚠️  | ⚠️  | ⚠️  |
| Completeness        | ❌  | ⚠️  | ✅  | ✅  | ✅  | ✅  |
| Root cause depth    | ❌  | ❌  | ❌  | ⚠️  | ⚠️  | ⚠️  |
| Cascade awareness   | ❌  | ❌  | ❌  | ❌  | ❌  | ❌  |
| Severity accuracy   | N/A | ⚠️  | ✅  | ✅  | ✅  | ✅  |
| Actionability       | ⚠️  | ⚠️  | ⚠️  | ✅  | ✅  | ✅  |
| Context usage       | N/A | N/A | ⚠️  | ✅  | ✅  | ✅  |

### 5.2 What Each Layer of Context Changed

**V1 (bare minimum — no context)**
- Input: Test failure log only
- Output: 3 categories, 8 separate bugs, generic root causes
- Helped: Nothing — baseline
- Missed: Everything beyond surface description

**V2 (+ output structure)**
- Added: Requested sections (title, severity, expected/actual, etc.)
- Helped: Format — sections clear, severity appeared, tests listed
- Missed: Root cause still guessing, no cascade, no context

**V3 (+ tech context + severity guide)**
- Added: "FastAPI CRUD app, SQLAlchemy, SQLite, Pydantic v2" + P0–P3 definitions
- Helped: Severity judgment — P1 justified ("breaks CRUD operation")
- Missed: Root cause still wrong, cascade still invisible

**V4 (+ system_overview.md)**
- Added: Full system documentation — architecture, code paths, user journey
- Helped: Code path tracing (AI referenced correct files/functions); actionability (project-specific code suggestions); root cause got closer — traced to `routers/todo.py`, identified serialization
- Missed: Still 4 wrong hypotheses. Almost touched ISS-004 but dismissed it. Cascade still invisible.

**V5 (+ evaluation_summary.md)**
- Added: Current system health — active risks, resolved issues, trend
- Helped: Health context — AI noted "aligns with existing risk landscape"; referenced ISS-006, ISS-007, ISS-002 in analysis
- Missed: Did NOT connect ISS-004 to the failures despite it being in the summary. Cascade still invisible. Root cause still hypothetical.

**V6 (+ issues_found.md)**
- Added: Full issue details — evidence, impact, fix recommendations
- Helped: Minimal additional value over V5; slightly better issue cross-referencing
- Missed: Still did not find the cascade. ISS-004 details were IN the input but AI did not connect "null title → corrupt record → serialization crash → 8 test failures."

### 5.3 Pattern — What Context Helps vs What It Doesn't

**Helps:**
| Context layer | What it improves |
|---|---|
| Structure | Format, completeness |
| Tech context | Severity judgment |
| System docs | Code path tracing, actionability |
| Health status | Cross-referencing existing issues |

**Does not help, at any dose:**
- Documentation volume → cascade awareness
- Documentation volume → runtime state diagnosis
- Documentation volume → connecting symptoms to a single root cause

**Key finding:** System documentation (V4) had the biggest positive impact — it's what turned vague guesses into project-specific, actionable code references. But every layer of context tested, including handing the AI the exact root cause in writing (V6), failed to produce cascade awareness. This points to a ceiling that isn't about context volume: root cause here lives in runtime state (a corrupted DB record), which no document — however detailed — encodes as an observable fact.

---

## 6. Failure Modes Identified

_Patterns of when and how AI output fails. Most valuable section for future reference._

### 6.0 The Core Finding

AI treated 8 test failures as 8 independent issues across all 6 versions. The real root cause is ONE issue — **ISS-004**: `PUT` with a null title creates a corrupt record in the DB, which causes a serialization crash on every subsequent `GET /todos/` call, cascading to break 8 tests.

AI could not find this because:

- **Root cause lives in runtime state, not code structure.** There is a corrupt record in the database. No amount of code reading or documentation reveals that. Only someone who ran the system, observed the 500, traced the error to serialization, then checked the DB would find it.
- **Cascade requires connecting across features.** The `PUT` endpoint creates the problem; the `GET` endpoint surfaces it. AI analyzed the `GET` failures in isolation — it never asked "what happened *before* these tests ran that could have corrupted the data?"

### 6.1 Failure Mode Catalog

| # | Mode | Description | Frequency | Example |
|---|------|------------|-----------|---------|
| FM-1 | Cascade blindness | AI treats N symptoms as N bugs instead of tracing to 1 root cause. | 6/6 versions | Every version reports the 8 test failures as 8 separate bugs. |
| FM-2 | Symptom-as-root-cause | AI says "unhandled exception" or "query parameter issue" — describes WHAT happens, not WHY it happens. | 6/6 versions | Root cause fields describe the crash, not the null-title write that caused it. |
| FM-3 | Hypothesis without verification | With more context, AI generates more hypotheses but cannot verify any of them. Lists multiple "probable causes" without evidence to rank them. | 3/6 versions (V4–V6, when context is rich) | V4–V6 each list ~4 probable causes with no way to distinguish which is real. |
| FM-4 | Near-miss dismissal | AI identifies "response serialization failure through TodoOut" as a hypothesis but dismisses it because "TodoCreate tests pass." Logic flaw: Create passing doesn't mean Read passes when the DB already contains corrupt data. | 1/6 versions (V4) — but most dangerous, since it looks like sound reasoning | V4's dismissal of the serialization hypothesis. |

### 6.2 Common Failure Patterns

- **State blindness:** AI can only reason over code and documentation — it never observes what's actually stored in the database at the time of failure. Any bug whose cause is accumulated runtime state (corrupt data, side effects, race conditions) is invisible to it, regardless of context depth.
- **Isolated symptom analysis:** AI evaluates each failing test/endpoint independently rather than asking what earlier operation could have produced the current state. This is why cascades across features (write endpoint corrupts data → read endpoint fails) are never detected.
- **Confident guessing dressed as diagnosis:** As context grows richer, the AI doesn't converge on the right answer — it produces more hypotheses, stated with reasoning that sounds plausible but isn't checked against evidence (FM-3, FM-4).

---

## 7. When NOT to Trust This Output

_Most important section for evaluator. Specific conditions where AI output should not be used without human verification._

### 7.1 High-Risk Conditions

_AI output should NOT be trusted when:_

- Multiple failures may share a root cause — AI will always treat them independently (FM-1, 6/6 versions).
- Root cause involves runtime state (corrupt data, accumulated side effects, race conditions) — AI can only read code, not observe state.
- AI lists multiple "probable causes" for the same failure — it's guessing, not diagnosing (FM-3).
- AI dismisses a hypothesis with logic that sounds reasonable but doesn't account for state (e.g. "tests pass elsewhere so serialization is fine" — FM-4). This is the most dangerous failure mode because it reads as sound reasoning.

### 7.2 Required Human Verification

_Even when output looks correct, always verify:_

- **Root cause analysis** — AI describes symptoms ("unhandled exception," "query parameter issue"), not the underlying cause, in 100% of versions tested.
- **Whether related failures share one origin** — check for a shared trigger (e.g. a prior write operation) before accepting N reported bugs as N independent issues.
- **Any dismissed hypothesis** — re-examine hypotheses the AI raised and then talked itself out of; V4 shows it can correctly surface the real cause and then reason its way away from it.
- **Runtime/DB state** — for any failure touching persisted data, inspect the actual data, not just the code path, before trusting the report.

### 7.3 Acceptable Use Cases

_AI output CAN be trusted for:_

- Formatting and structuring raw test output into a readable, well-sectioned report (V2 onward).
- Severity assessment, when given proper domain context and a severity guide (V3 onward — became reliable and stayed reliable through V6).
- Identifying which files and functions are involved, when given system documentation (V4 onward).
- Initial triage of a single, isolated failure with a clear, self-contained error message — not a batch of failures that might be related.

---

## 8. Recommendations

### 8.1 For This Tool

_Specific improvements for the AI tool evaluated:_

- Do not use this tool's output as a final bug report when the input contains more than one failing test — require a human pass specifically to check for a shared root cause before the report is filed.
- Add an explicit step in the prompt asking the AI to check, for each write endpoint, whether any prior write in the session could have produced the state now causing read failures — this won't fully solve cascade blindness (V6 shows even the answer in the input doesn't trigger it) but may reduce it.
- Do not feed it more documentation expecting root-cause or cascade quality to improve — V4→V6 shows this plateaus. Spend that effort on system docs (biggest ROI, per §5.3) and stop there; further gains need a different mechanism (e.g. giving the AI direct DB/log query access), not more static text.
- Flag any hypothesis the AI raises and then dismisses (FM-4) for mandatory human review — the dismissal reasoning is often exactly where the AI was closest to correct.

### 8.2 For AI Integration Generally

_Lessons that apply to any AI integration:_

- Context quality has diminishing, then zero, returns for specific criteria. Formatting, severity judgment, and code-path tracing all improved with the right context layer and then plateaued (V2–V4). Root cause depth and cascade awareness never moved, even when the answer was placed directly in the input (V6) — more context is not a substitute for the ability to observe runtime state.
- A model that reasons only over static text (code + docs) cannot diagnose bugs whose cause is a fact about the running system (corrupt data, in-memory state, timing). If diagnosing those bugs matters, the integration needs tool access to observe state (DB queries, live logs), not just richer prompts.
- Watch for confident-sounding dismissals of correct hypotheses — this is more dangerous than an obviously wrong answer because it passes casual review.
- Human evaluators are specifically needed for cascade detection, state observation, and root cause verification — this is the gap a human Eval Engineer role exists to fill; do not assume it closes as prompts/context improve.

---

## 9. Evaluation Metadata

| Item | Value |
|------|-------|
| Evaluator | Noah Ho |
| Date | 2026-07-03 |
| Model used | Haiku 4.5 |
| Total cases | 6 (V1–V6) |
| Total prompt versions | 6 |
| Time spent | 1 hour |
| Cost | $0.34 |