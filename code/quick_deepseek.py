import requests
import os

# Set API key directly in the script
api_key = "sk-7dff725207d44c71b12374519af394e7"

# Get user input
prompt = input("Enter your prompt: ")

# Set up the API request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 1000,
    "temperature": 0.7
}

print("\nSending request to DeepSeek...\n")

# Make the API request
response = requests.post(
    "https://api.deepseek.com/v1/chat/completions", 
    headers=headers, 
    json=data
)

# Display the response
if response.status_code == 200:
    result = response.json()
    if "choices" in result and len(result["choices"]) > 0:
        if "message" in result["choices"][0]:
            print(result["choices"][0]["message"]["content"])
        else:
            print("Unexpected response format")
    else:
        print("No choices in response")
else:
    print(f"Error: {response.status_code}")
    print(response.text) 