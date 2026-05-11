import requests, time

url = "https://jsonplaceholder.typicode.com/users/1"
start = time.time()
response = requests.get(url)
data = response.json()
elapsed = round((time.time() - start) * 1000)

print(f"URL: {url}")
print(f"Status Code: {response.status_code}")
print(f"Response time: {elapsed} milliseconds")

print("Response summary:")
print(f" - Id: {data.get('id')}")
print(f" - Name: {data.get('name')}")
print(f" - Email: {data.get('email')}")
print(f" - Company: {data.get('company').get('name')}")
