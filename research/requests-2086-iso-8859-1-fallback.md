## Issue Analysis: Remove ISO-8859-1 charset fallback — #2086
**Repo:** psf/requests  
**Link:** https://github.com/psf/requests/issues/2086  
**Opened:** January 7, 2014  
**Status:** Open (still active as of 2024)  

---

## Layer 1 — System

### Symptom
When an HTTP response does not declare a charset in the `Content-Type` 
header, the `requests` library automatically falls back to ISO-8859-1 
encoding — following the old RFC 2616 standard.

This causes `response.text` to return incorrectly decoded text for any 
server that sends UTF-8 content without explicitly declaring it — which 
is extremely common in practice.

### Root cause
RFC 2616 (the old HTTP standard) mandated ISO-8859-1 as the default 
charset for text content. The `requests` library implemented this rule. 
However, RFC 2616 has since been replaced by RFC 7231, which removes 
this default entirely. The `requests` library has not been updated to 
reflect this change.

### Why still unresolved after 9+ years
The fix itself is technically simple — remove the fallback. The blocker 
is backward compatibility. `requests` is one of the most downloaded 
Python packages. Any code that currently relies on the ISO-8859-1 
fallback behavior would silently break after the change. No maintainer 
wants to own that risk without a clear migration path or a major version 
bump.

### Fix approaches discussed
- Remove the fallback entirely
- Make the fallback configurable — opt-in rather than default
- Return raw bytes and let the caller decide encoding
- No consensus reached across 9 years of discussion

---

## Layer 2 — People

### Who reported it
lukasa — a core maintainer of the `requests` library — opened the issue 
himself. This is unusual: typically issues are reported by users, not 
maintainers. It signals that the team was already aware this was 
technically wrong but hadn't acted on it.

### Who has authority
lukasa and kennethreitz appear to be the core decision-makers. Their 
comments carry the most weight in the thread.

### Disagreements
The main disagreement is not about whether the behavior is wrong — 
everyone agrees ISO-8859-1 fallback is incorrect. The disagreement is 
about what to replace it with and how to handle the breaking change 
responsibly.

Several contributors proposed different approaches over the years, but 
no single proposal gained enough consensus to be merged.

### Domain experts in the thread
lukasa demonstrates the deepest technical knowledge — referencing 
specific RFC numbers, explaining the HTTP spec evolution, and 
anticipating edge cases. Other contributors largely defer to his 
technical assessment.

---

## Layer 3 — Culture

### How the team handles long-running issues
This issue has been open for over 9 years with periodic resurrection — 
new contributors discover the issue, read only recent comments without 
full context, and re-raise points that were already discussed years 
earlier. The maintainers respond patiently but the cycle repeats.

This suggests the team values stability and backward compatibility 
heavily over shipping fast. They will not merge a breaking change until 
there is clear consensus — even if that takes years.

### Response speed
Maintainers respond relatively quickly to new comments — usually within 
days or weeks. However, responding is different from resolving. The team 
is engaged but not willing to force a decision.

### Breaking change culture
The thread makes it clear that `requests` maintainers are extremely 
conservative about breaking changes. The library is used by millions of 
projects. This conservatism is justified but it also means technically 
wrong behavior can persist for years when fixing it would break 
backward compatibility.

### What this tells you about joining this team
If you were onboarding onto the `requests` team, this issue would tell 
you immediately:
- Correctness matters but stability matters more
- Decisions require broad consensus, not individual authority
- Long-running issues are expected — patience is a cultural value
- New contributors are welcomed but expected to read full history 
  before commenting

---

## My Assessment

This issue should be resolved in the next major version bump with a 
clear deprecation warning in the current version. The technical fix is 
straightforward. The real work is communication — notifying the 
ecosystem, providing a migration guide, and giving users time to adapt.

The fact that it has remained open for 9 years is not a failure of the 
team — it reflects the genuine difficulty of maintaining critical 
infrastructure that millions of projects depend on. Every decision has 
real consequences at that scale.

---

## Relevance to qa-toolkit
`requests` is used directly in `api_checker.py`. If any API being 
monitored returns text content without declaring charset, 
`response.text` may silently return incorrectly decoded data — and 
`api_checker.py` would not detect this. A future improvement could add 
charset validation to the response check.