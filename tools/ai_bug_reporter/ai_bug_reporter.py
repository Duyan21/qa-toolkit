# tools/ai_bug_reporter.py
import anthropic
import os
import sys
import json

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

PROMPTS = {
    "v1": """
Here is a test failure output:

{failure}

Write a bug report for this failure.
""",
    "v2": """
Here is a test failure output:

{failure}

Write a bug report with the following sections:
- Title: one-line summary
- Severity: P0/P1/P2/P3
- What happened: describe the failure
- Expected vs Actual
- Root cause analysis
- Recommendation
""",
    "v3": """
You are a QA evaluator reviewing a software system.
{context}

Severity guide:
- P0: System unusable, no workaround
- P1: Core feature broken
- P2: Non-critical, affects experience
- P3: Minor, cosmetic

Here is a test failure output:

{failure}

Write a bug report with the following sections:
- Title: one-line summary
- Severity: P0/P1/P2/P3 with justification
- What happened
- Expected vs Actual
- Root cause analysis
- Impact
- Recommendation with code suggestion if possible
""",
    "v4": """
You are a QA evaluator reviewing a software system.

System overview:
{system_overview}

{context}

Severity guide:
- P0: System unusable, no workaround
- P1: Core feature broken
- P2: Non-critical, affects experience
- P3: Minor, cosmetic

Here is a test failure output:

{failure}

Write a bug report with the following sections:
- Title: one-line summary
- Severity: P0/P1/P2/P3 with justification
- What happened
- Expected vs Actual
- Root cause analysis
- Impact
- Recommendation with code suggestion if possible
""",
"v5": """
You are a QA evaluator reviewing a software system.

System overview:
{system_overview}

Current system health/status:
{system_status}

{context}

Severity guide:
- P0: System unusable, no workaround
- P1: Core feature broken
- P2: Non-critical, affects experience
- P3: Minor, cosmetic

Here is a test failure output:

{failure}

Write a bug report with the following sections:
- Title: one-line summary
- Severity: P0/P1/P2/P3 with justification, informed by current system health
- What happened
- Expected vs Actual
- Root cause analysis (consider whether system health explains or rules out likely causes)
- Impact
- Recommendation with code suggestion if possible
""",
"v6": """
You are a QA evaluator reviewing a software system.

System overview:
{system_overview}

Current system health/status:
{system_status}

Current system issues:
{system_issues}

{context}

Severity guide:
- P0: System unusable, no workaround
- P1: Core feature broken
- P2: Non-critical, affects experience
- P3: Minor, cosmetic

Here is a test failure output:

{failure}

Write a bug report with the following sections:
- Title: one-line summary
- Severity: P0/P1/P2/P3 with justification, informed by current system health
- What happened
- Expected vs Actual
- Root cause analysis (consider whether system health explains or rules out likely causes)
- Impact
- Recommendation with code suggestion if possible
""",
}


def read_file(filepath):
    with open(filepath, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xff\xfe"):
        encoding = "utf-16-le"
    elif raw.startswith(b"\xfe\xff"):
        encoding = "utf-16-be"
    elif raw.startswith(b"\xef\xbb\xbf"):
        encoding = "utf-8-sig"
    else:
        encoding = "utf-8"
    return raw.decode(encoding).lstrip(chr(0xFEFF))


def generate_report(prompt, model="claude-haiku-4-5-20251001"):
    message = client.messages.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )
    return "".join(
        block.text for block in message.content
        if hasattr(block, "text")
    )


def run(failure_file, version="v1", context="", system_overview_file=None, system_status_file=None, system_issues_file=None, model="claude-haiku-4-5-20251001"):
    failure = read_file(failure_file)

    kwargs = {"failure": failure, "context": context}

    if version == "v4":
        if not system_overview_file:
            raise ValueError("version 'v4' requires --system-overview <path>")
        kwargs["system_overview"] = read_file(system_overview_file)
    if version == "v5":
        if not system_overview_file or not system_status_file:
            raise ValueError("version 'v5' requires --system-overview <path> and --system-status <path>")
        kwargs["system_overview"] = read_file(system_overview_file)
        kwargs["system_status"] = read_file(system_status_file)

    if version == "v6":
        if not system_overview_file or not system_status_file or not system_issues_file:
            raise ValueError("version 'v6' requires --system-overview <path> and --system-status <path> and --system-issues <path>")
        kwargs["system_overview"] = read_file(system_overview_file)
        kwargs["system_status"] = read_file(system_status_file)
        kwargs["system_issues"] = read_file(system_issues_file) if system_issues_file else "No known issues."

        if hasattr(args, "system_issues_file") and args.system_issues_file:
            kwargs["system_issues"] = read_file(args.system_issues_file)
        else:
            kwargs["system_issues"] = "No known issues."

    prompt = PROMPTS[version].format(**kwargs)
    return generate_report(prompt, model)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Bug Reporter")
    parser.add_argument("failure_file", help="Path to test failure output")
    parser.add_argument("--version", default="v1", choices=PROMPTS.keys())
    parser.add_argument("--context", default="", help="System context string")
    parser.add_argument("--system-overview", default=None,
                        help="Path to system_overview.md")
    parser.add_argument("--system-status", default=None,
                        help="Path to evaluation_summary.md")
    parser.add_argument("--system-issues", default=None,
                        help="Path to issues_found.md")
    parser.add_argument("--model", default="claude-haiku-4-5-20251001")

    args = parser.parse_args()

    report = run(
        args.failure_file,
        version=args.version,
        context=args.context,
        system_overview_file=args.system_overview,
        system_status_file=args.system_status,
        system_issues_file=args.system_issues,
        model=args.model
    )
    print(report)
