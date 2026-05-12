import requests, time
from datetime import datetime

# url = "https://jsonplaceholder.typicode.com/users/1"
# start = time.time()
# response = requests.get(url)
# data = response.json()
# elapsed = round((time.time() - start) * 1000)

# print(f"URL: {url}")
# print(f"Status Code: {response.status_code}")
# print(f"Response time: {elapsed} milliseconds")

# print("Response summary:")
# print(f" - Id: {data.get('id')}")
# print(f" - Name: {data.get('name')}")
# print(f" - Email: {data.get('email')}")
# print(f" - Company: {data.get('company').get('name')}")

def check_api(url, log_file):
    # Measure response time
    start = time.time()
    response = requests.get(url)
    elapsed = round((time.time() - start) * 1000)

    # Number of fields in the response JSON
    try:
        data = response.json()
        fields = len(data.keys())
    except (ValueError, AttributeError):
        fields = "N/A"

     # Status code check
    THRESHOLD_MS = 500
    if response.status_code != 200:
        status_icon = "❌"
    elif elapsed > THRESHOLD_MS:
        status_icon = "⚠️"
    else:
        status_icon = "✅"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"{timestamp} | Checked API: {url} | Status: {response.status_code} {status_icon} | Response time: {elapsed} ms | Fields: {fields}"
    print(line)
    log_file.write(line + "\n")

with open("api_health.log", "w", encoding="utf-8") as log_file:
    check_api("https://api.github.com/users/torvalds", log_file)
    check_api("https://api.github.com/repos/facebook/react", log_file)
    check_api("https://jsonplaceholder.typicode.com/users/1", log_file)


