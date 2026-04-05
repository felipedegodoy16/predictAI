import urllib.request
import json

url = "http://127.0.0.1:8000/api/auth/login/"
data = json.dumps({"email": "admin@predictai.com", "password": "admin"}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.status}")
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"Erro HTTP: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Erro: {e}")
