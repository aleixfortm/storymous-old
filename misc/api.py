from misc.config import API_ENDPOINT
import requests


stories_api = requests.get(API_ENDPOINT)
if stories_api.status_code == 200:
    test_stories = stories_api.json()
else:
    print("\nError: API request failed with status code\n", stories_api.status_code)