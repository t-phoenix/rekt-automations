from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("TWITTERAPI_IO_KEY")

headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
resp = requests.get(
    "https://api.twitterapi.io/twitter/user/last_tweets",
    headers=headers,
    params={"userName": "sharpinvestr", "limit": 10},
    timeout=15,
)
data = resp.json()
import json
tweets = data.get("data", {}).get("tweets", [])
if tweets:
    tw = tweets[0]
    author = tw.get("author", tw.get("user", {}))
    print("KEYS in tweet:", tw.keys())
    print("KEYS in author:", author.keys())
    print("Followers:", author.get("followers", author.get("followersCount")))
