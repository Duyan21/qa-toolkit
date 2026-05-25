import requests
import time
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

THRESHOLD_MS = 500


def check_api(url, log_file=None, threshold_ms=THRESHOLD_MS):
    start = time.time()
    response = requests.get(url)
    elapsed = round((time.time() - start) * 1000)

    try:
        data = response.json()
        fields = len(data.keys())
    except (ValueError, AttributeError):
        fields = "N/A"

    if response.status_code >= 500:
        status_icon = "❌"
        hint = "-> Runbook: runbooks/debug-5xx.md"
    elif response.status_code >= 400:
        status_icon = "❌"
        hint = "-> Runbook: runbooks/debug-4xx.md"
    elif elapsed > threshold_ms:
        status_icon = "⚠️"
        hint = "-> Runbook: runbooks/debug-slow-api.md"
    else:
        status_icon = "✅"
        hint = None

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"{timestamp} | Checked API: {url} | Status: {response.status_code} {status_icon}"
        f" | Response time: {elapsed} ms | Fields: {fields}"
    )

    print(line)
    if log_file:
        log_file.write(line + "\n")
    if hint:
        print(f"   {hint}")

    return {
        "url": url,
        "status_code": response.status_code,
        "elapsed_ms": elapsed,
        "fields": fields,
        "status_icon": status_icon,
        "hint": hint,
    }


if __name__ == "__main__":
    with open("api_health.log", "w", encoding="utf-8") as log_file:
        check_api("https://api.github.com/users/torvalds", log_file)
        check_api("https://api.github.com/repos/facebook/react", log_file)
        check_api("https://jsonplaceholder.typicode.com/users/1", log_file)
