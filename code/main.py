import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug - print to verify the key is loaded
print(f"DeepSeek API Key detected: {'Yes' if os.getenv('DEEPSEEK_API_KEY') else 'No'}") 