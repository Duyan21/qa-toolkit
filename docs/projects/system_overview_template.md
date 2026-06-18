# System Overview — [Project Name]

> **Evaluated by:** An Ho  
> **Date:** [YYYY-MM-DD]  
> **Project repo:** [link]  
> **Purpose of this doc:** Structured evaluation of an external system — domain, functionality, and technical assessment.

---

## How to use this template

- **Write sections that have substance.** Don't fill for the sake of filling.
- **Skip sections that don't apply** — but write 1 line explaining why you skipped.
- **Small project:** template is a thinking checklist, output is concise.
- **Large project:** template is a skeleton, output is comprehensive.

---

## Section 1: Product Identity

### 1.1 What — What is this product?

_One paragraph. What does it do, in plain language._

### 1.2 Why — Why does it exist?

_What problem does it solve? What motivated its creation?_

### 1.3 Who — Who uses it?

_Target users. If README doesn't say, state your assumption explicitly._

**Skipped sections & reasons:**
- 1.4 Ecosystem — _[reason, e.g. "Standalone project, no ecosystem"]_
- 1.5 Lifecycle — _[reason]_
- 1.6 Ownership — _[reason]_

---

## Section 2: Business Perspective

### 2.1 End-to-End User Journey

_What does a user do from start to finish? Keep it simple — no technical terms._

### 2.2 Product Scope & Boundaries

_What it does AND what it explicitly does NOT do. Boundaries matter as much as features._

**Skipped sections & reasons:**
- 2.3 Core Business Capabilities — _[reason, e.g. "Tutorial project, no business logic beyond CRUD"]_
- 2.4 Variants — _[reason]_
- 2.5 Compliance — _[reason]_

---

## Section 3: Technology Perspective

### 3.1 Architecture Diagram

_Include if meaningful. Skip with reason if the system is too simple to diagram._

### 3.2 Codebase Structure

_Folder/file structure. What lives where. Entry point._

```
[paste tree output or describe manually]
```

### 3.3 Key Technology Decisions

_What tech stack was chosen and — if you can infer — why. Note anything unusual or notable._

**Skipped sections & reasons:**
- 3.4 Integration Landscape — _[reason]_

---

## Section 4: The Bridge — End-to-End Trace

### 4.1 One Request, Start to Finish

_Pick one operation (e.g. "create a note"). Trace it from HTTP request → route → logic → database → response. This is the most valuable section — it proves you understand how the system actually works._

```
[Request] → [Route/Handler] → [Business Logic] → [Database] → [Response]
```

---

## Section 5: Documentation Quality Assessment

_How well does the README/docs serve someone evaluating this system?_

### What's well documented:
- _[list]_

### What's missing or unclear:
- _[list — each item is a finding]_

### What's mixed together that should be separated:
- _[list — e.g. "Features, infrastructure, and API docs are in one section"]_

---

## Section 6: Quick Reference

### 6.1 How to run

```bash
[commands to get the project running locally]
```

### 6.2 Key endpoints / interfaces

| Method | Path | Description |
|--------|------|-------------|
| | | |

### 6.3 Glossary

_Only if the project uses domain-specific terms that need definition. Otherwise skip._

---

## Assumptions Log

_Everything you assumed because documentation didn't state it explicitly. Mark each as [CONFIRMED] or [UNCONFIRMED] after reading code._

| # | Assumption | Source | Status |
|---|-----------|--------|--------|
| 1 | | README / inference | ⏳ |
| 2 | | | ⏳ |

---

## Open Questions

_Things you still don't know after reading README + running the app. These drive your code reading in Step 7._

1. _[question]_
2. _[question]_
