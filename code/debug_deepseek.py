import requests
import os
import time
import sys

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
print(f"Using API endpoint: https://api.deepseek.com/v1/chat/completions")
print(f"API key (first 4 chars): {api_key[:4]}...")

# Add a timeout to prevent hanging indefinitely
try:
    start_time = time.time()
    
    # Make the API request with a 30-second timeout
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions", 
        headers=headers, 
        json=data,
        timeout=30  # 30 second timeout
    )
    
    end_time = time.time()
    print(f"\nRequest completed in {end_time - start_time:.2f} seconds")
    
    # Display the response
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            if "message" in result["choices"][0]:
                print("\n--- DEEPSEEK RESPONSE ---\n")
                print(result["choices"][0]["message"]["content"])
                print("\n------------------------\n")
            else:
                print(f"Unexpected response format: {result}")
        else:
            print(f"No choices in response: {result}")
    else:
        print(f"Error response: {response.text}")

except requests.exceptions.Timeout:
    print("\nERROR: Request timed out after 30 seconds")
    print("This usually indicates network issues or API service problems")
    
except requests.exceptions.ConnectionError:
    print("\nERROR: Connection failed")
    print("This could be due to network issues or incorrect API endpoint")
    
except Exception as e:
    print(f"\nUnexpected error: {type(e).__name__}: {e}")

print("\nDone") 