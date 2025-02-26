import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
}

try:
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions", 
        headers=headers, 
        json=data
    )
    
    print(f"Status code: {response.status_code}")
    print("Response:")
    print(response.json())
except Exception as e:
    print(f"Error: {e}") 