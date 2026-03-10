import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("TWITTERAPI_IO_KEY", "")

url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
params = {
    "query": "(crypto) since:2024-03-01",
    "queryType": "Top",
    "cursor": ""
}

r = requests.get(url, headers=headers, params=params)
if r.status_code == 200:
    data = r.json()
    tweets = data.get("tweets", [])
    if tweets:
        print(json.dumps(tweets[0], indent=2))
    else:
        print("No tweets found.")
else:
    print(r.text)

