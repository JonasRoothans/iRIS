import requests

url = "https://raadsinformatie.eindhoven.nl"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, headers=headers, timeout=30)
    print("SUCCESS:", r.status_code)
except Exception as e:
    print("FAILED:", e)