import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("TWITTERAPI_IO_KEY", "")
print("Using API Key length:", len(api_key))

url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
params = {
    "query": "(crypto OR bitcoin) since:2024-03-01",
    "queryType": "Top",
}

print("Testing without cursor parameter...")
r1 = requests.get(url, headers=headers, params=params)
print("r1.status_code:", r1.status_code)
if r1.status_code != 200:
    print(r1.text)

print("Testing with cursor=''...")
params["cursor"] = ""
r2 = requests.get(url, headers=headers, params=params)
print("r2.status_code:", r2.status_code)
if r2.status_code != 200:
    print(r2.text)

