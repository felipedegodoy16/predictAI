import urllib.request
import urllib.error
import json
import os

token = ""

# I don't have the token, but I can check if it returns 401 or 404 or something else
try:
    req = urllib.request.Request(
        "http://localhost:8000/api/work-orders/1/move_status/",
        data=json.dumps({"status": 2}).encode('utf-8'),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code} - {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
