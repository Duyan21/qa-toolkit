import os, sys

sys.stdout.reconfigure(encoding="utf-8")

def analyze_log_file(log_file_path):
    passed_api = 0
    slow_api = 0
    failed_api = 0

    slow_apis = {}
    failed_4xx = {}
    failed_5xx = {}

    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "Response time: " not in line:
                response_time = "N/A"
            else:
                response_time = int(line.split("Response time: ")[1].split(" ms")[0])

            api_url = line.split("Checked API: ")[1].split(" | ")[0]
            status_code = int(line.split("Status: ")[1].split(" ")[0])

            if "✅" in line:
                passed_api += 1
            elif "⚠️" in line:
                slow_api += 1
                slow_apis[api_url] = response_time
            elif "❌" in line:
                failed_api += 1
                if status_code >= 500:
                    failed_5xx[api_url] = (status_code, response_time)
                else:
                    failed_4xx[api_url] = (status_code, response_time)

    print(f"Total API checks: {passed_api + slow_api + failed_api}")
    print(f"Passed: {passed_api} ✅")
    print(f"Slow:   {slow_api} ⚠️")
    print(f"Failed: {failed_api} ❌")

    if slow_apis:
        print("\n=== Slow APIs ⚠️ ===")
        for api, response_time in slow_apis.items():
            print(f" - {api} (Response time: {response_time} ms)")
        print(f" -> Runbook: runbooks/debug-slow-api.md")

    if failed_5xx:
        print("\n=== Failed APIs 5xx ❌ ===")
        for api, (code, response_time) in failed_5xx.items():
            print(f" - [{code}] {api} (Response time: {response_time} ms)")
        print(f" -> Runbook: runbooks/debug-5xx.md")

    if failed_4xx:
        print("\n=== Failed APIs 4xx ❌ ===")
        for api, (code, response_time) in failed_4xx.items():
            print(f" - [{code}] {api} (Response time: {response_time} ms)")
        print(f" -> Runbook: runbooks/debug-4xx.md")

log_path = os.path.join(os.path.dirname(__file__), 'api_health.log')
analyze_log_file(log_path)