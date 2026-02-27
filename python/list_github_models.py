import os
import requests
from dotenv import load_dotenv

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")
AI_API_BASE = os.getenv("AI_API_BASE")

url = f"{AI_API_BASE}/models"

headers = {
    "Authorization": f"Bearer {AI_API_KEY}",
    "X-GitHub-Api-Version": "2024-10-14"
}

resp = requests.get(url, headers=headers)
print("STATUS:", resp.status_code)
print(resp.text)