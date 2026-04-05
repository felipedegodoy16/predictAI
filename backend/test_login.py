import requests

url = "http://127.0.0.01:8000/api/auth/login/"
payload = {"email": "admin@predictai.com", "password": "admin"}
try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Erro: {e}")
