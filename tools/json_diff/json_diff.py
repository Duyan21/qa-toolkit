import json
from enum import Enum


class DiffStatus(str, Enum):
    IDENTICAL             = "identical"
    MISSING_IN_PRODUCTION = "missing_in_production"
    EXTRA_IN_PRODUCTION   = "extra_in_production"
    VALUE_DIFF            = "value_diff"
    TYPE_MISMATCH         = "type_mismatch"
    WHITESPACE_DIFF       = "whitespace_diff"
    ARRAY_DIFF            = "array_diff"
    ARRAY_LENGTH_DIFF     = "array_length_diff"


BUCKET_MAP = {
    DiffStatus.IDENTICAL:             "identical",
    DiffStatus.MISSING_IN_PRODUCTION: "missing_in_production",
    DiffStatus.EXTRA_IN_PRODUCTION:   "extra_in_production",
    DiffStatus.VALUE_DIFF:            "different",
    DiffStatus.TYPE_MISMATCH:         "different",
    DiffStatus.WHITESPACE_DIFF:       "different",
    DiffStatus.ARRAY_DIFF:            "different",
    DiffStatus.ARRAY_LENGTH_DIFF:     "different",
}


def _diff_recursive(path, val1, val2, ignore_array_order=False):
    results = []

    if type(val1) is not type(val2):
        results.append({
            "path": path,
            "status": DiffStatus.TYPE_MISMATCH,
            "staging": val1,
            "production": val2,
            "staging_type": type(val1).__name__,
            "production_type": type(val2).__name__,
        })
        return results

    if isinstance(val1, dict):
        for k in val1:
            child = f"{path}.{k}"
            if k not in val2:
                entry = {"path": child, "status": DiffStatus.MISSING_IN_PRODUCTION, "staging": val1[k]}
                if val1[k] is None:
                    entry["note"] = "staging key is explicitly null"
                results.append(entry)
            else:
                results.extend(_diff_recursive(child, val1[k], val2[k], ignore_array_order))
        for k in val2:
            if k not in val1:
                child = f"{path}.{k}"
                entry = {"path": child, "status": DiffStatus.EXTRA_IN_PRODUCTION, "production": val2[k]}
                if val2[k] is None:
                    entry["note"] = "production key is explicitly null"
                results.append(entry)

    elif isinstance(val1, list):
        if ignore_array_order:
            set1 = {json.dumps(x, sort_keys=True) for x in val1}
            set2 = {json.dumps(x, sort_keys=True) for x in val2}
            only_staging = [json.loads(x) for x in set1 - set2]
            only_prod = [json.loads(x) for x in set2 - set1]
            if only_staging or only_prod:
                results.append({
                    "path": path,
                    "status": DiffStatus.ARRAY_DIFF,
                    "only_in_staging": only_staging,
                    "only_in_production": only_prod,
                })
            else:
                results.append({"path": path, "status": DiffStatus.IDENTICAL, "value": val1})
        else:
            if len(val1) != len(val2):
                results.append({
                    "path": path,
                    "status": DiffStatus.ARRAY_LENGTH_DIFF,
                    "staging_length": len(val1),
                    "production_length": len(val2),
                })
            else:
                for i, (a, b) in enumerate(zip(val1, val2)):
                    results.extend(_diff_recursive(f"{path}[{i}]", a, b, ignore_array_order))

    else:
        if val1 == val2:
            results.append({"path": path, "status": DiffStatus.IDENTICAL, "value": val1})
        else:
            is_whitespace_only = (
                isinstance(val1, str)
                and isinstance(val2, str)
                and val1.strip() == val2.strip()
            )
            results.append({
                "path": path,
                "status": DiffStatus.WHITESPACE_DIFF if is_whitespace_only else DiffStatus.VALUE_DIFF,
                "staging": val1,
                "production": val2,
            })

    return results


def json_diff(stagingJson, productionJson, ignore_array_order=False):
    with open(stagingJson, "r") as f1, open(productionJson, "r") as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    if type(data1) is not type(data2):
        return {
            "summary": {"identical": 0, "different": 1, "missing_in_production": 0, "extra_in_production": 0},
            "identical": [],
            "different": [{
                "path": "$",
                "status": DiffStatus.TYPE_MISMATCH,
                "staging": data1,
                "production": data2,
                "staging_type": type(data1).__name__,
                "production_type": type(data2).__name__,
            }],
            "missing_in_production": [],
            "extra_in_production": [],
        }

    all_entries = _diff_recursive("$", data1, data2, ignore_array_order)

    report = {"identical": [], "different": [], "missing_in_production": [], "extra_in_production": []}

    for entry in all_entries:
        bucket = BUCKET_MAP.get(entry["status"])
        if bucket is None:
            raise ValueError(
                f"Unhandled status '{entry['status']}' — add it to DiffStatus and BUCKET_MAP"
            )
        report[bucket].append(entry)

    report["summary"] = {
        "identical": len(report["identical"]),
        "different": len(report["different"]),
        "missing_in_production": len(report["missing_in_production"]),
        "extra_in_production": len(report["extra_in_production"]),
    }

    return report


def print_diff(report):
    summary = report["summary"]
    print(
        f"Summary — identical: {summary['identical']}  |  "
        f"different: {summary['different']}  |  "
        f"missing in production: {summary['missing_in_production']}  |  "
        f"extra in production: {summary['extra_in_production']}"
    )

    if report["missing_in_production"]:
        print(f"\nMissing in production ({summary['missing_in_production']}):")
        for d in report["missing_in_production"]:
            note = f"  [{d['note']}]" if "note" in d else ""
            print(f"  - {d['path']}: staging={d['staging']!r}{note}")

    if report["extra_in_production"]:
        print(f"\nExtra in production ({summary['extra_in_production']}):")
        for d in report["extra_in_production"]:
            note = f"  [{d['note']}]" if "note" in d else ""
            print(f"  + {d['path']}: production={d['production']!r}{note}")

    if report["different"]:
        print(f"\nDifferent ({summary['different']}):")
        for d in report["different"]:
            status = d["status"]
            if status == DiffStatus.TYPE_MISMATCH:
                print(f"  ~ {d['path']}: {d['staging_type']}({d['staging']!r}) vs {d['production_type']}({d['production']!r})")
            elif status == DiffStatus.VALUE_DIFF:
                print(f"  ~ {d['path']}: staging={d['staging']!r} vs production={d['production']!r}")
            elif status == DiffStatus.WHITESPACE_DIFF:
                print(f"  ~ {d['path']}: whitespace only — staging={d['staging']!r} vs production={d['production']!r}")
            elif status == DiffStatus.ARRAY_DIFF:
                print(f"  ~ {d['path']}: only_in_staging={d['only_in_staging']}  only_in_production={d['only_in_production']}")
            elif status == DiffStatus.ARRAY_LENGTH_DIFF:
                print(f"  ~ {d['path']}: staging={d['staging_length']} items vs production={d['production_length']} items")

    if report["identical"]:
        print(f"\nIdentical ({summary['identical']}):")
        for d in report["identical"]:
            print(f"  = {d['path']}: {d['value']!r}")

    has_issues = summary["different"] or summary["missing_in_production"] or summary["extra_in_production"]
    print(f"\n-> Runbook: runbooks/debug-json-mismatch.md" if has_issues else "\nNo differences found.")


if __name__ == "__main__":
    result = json_diff('staging.json', 'production.json')
    print_diff(result)
