from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("TWITTERAPI_IO_KEY")
print("API KEY length:", len(api_key) if api_key else 0)

headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
query = "(memecoin OR crypto OR pumpfun OR solana) min_faves:50 -filter:replies"
resp = requests.get(
    "https://api.twitterapi.io/twitter/tweet/advanced_search",
    headers=headers,
    params={"query": query, "queryType": "Latest"},
    timeout=15,
)
data = resp.json()
for tw in data.get("tweets", [])[:2]:
    print(tw.keys())
    author = tw.get("author", tw.get("user", {}))
    print("UserName is:", author.get("userName"))
