import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('TWITTERAPI_IO_KEY', '')

url = 'https://api.twitterapi.io/twitter/tweet/advanced_search'
headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}
query = "(memecoin OR memecoins OR shitcoin OR 100x OR gem OR moon OR rekt OR liquidations OR rugged OR rugpull OR pump OR ape OR degen) since:2026-03-06 min_faves:500 -filter:replies"

params = {
    'query': query,
    'queryType': 'Top',
    'cursor': ''
}

r = requests.get(url, headers=headers, params=params)
print("Status:", r.status_code)
if r.status_code != 200:
    print(r.text)

