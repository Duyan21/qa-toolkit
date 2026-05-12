import os

def analyze_log_file(log_file_path):
    passed_api = 0
    slow_api = 0
    failed_api = 0

    slow_apis = {}
    failed_apis = {}
    
    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "Response time: " not in line:
                response_time = "N/A"
            else:
                response_time = int(line.split("Response time: ")[1].split(" ms")[0])

            api_url = line.split("Checked API: ")[1].split(" | ")[0]
            
            if "✅" in line:
                passed_api += 1
            elif "⚠️" in line:
                slow_api += 1
                slow_apis[api_url] = response_time
            elif "❌" in line:
                failed_api += 1
                failed_apis[api_url] = response_time

    print(f"Total API checks: {passed_api + slow_api + failed_api}")
    print(f"Total passed APIs: {passed_api} ✅")
    print(f"Total slow APIs: {slow_api} ⚠️")
    print(f"Total failed APIs: {failed_api} ❌")

    if slow_apis:
        print("\n === Slow APIs ⚠️ ===")
        for api, response_time in slow_apis.items():
            print(f" - {api} (Response time: {response_time} ms)")

    if failed_apis:
        print("\n === Failed APIs ❌ ===")
        for api, response_time in failed_apis.items():
            print(f" - {api} (Response time: {response_time} ms)")

log_path = os.path.join(os.path.dirname(__file__), '..', 'api_checker', 'api_health.log')
analyze_log_file(log_path)