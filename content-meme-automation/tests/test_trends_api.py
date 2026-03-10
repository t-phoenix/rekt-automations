import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('TWITTERAPI_IO_KEY', '')

url = 'https://api.twitterapi.io/twitter/trends'
headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}
params = {'woeid': 1}

r = requests.get(url, headers=headers, params=params)
print("Trends Status:", r.status_code)
if r.status_code != 200:
    print(r.text)
