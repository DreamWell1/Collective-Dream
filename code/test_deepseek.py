#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for DeepSeek API using OpenAI client library.
"""

import os
import sys
from openai import OpenAI

def test_deepseek():
    """Test the DeepSeek API using OpenAI client."""
    
    # Get API key from environment or use the hardcoded value
    api_key = os.environ.get("DEEPSEEK_API_KEY", "sk-7dff725207d44c71b12374519af394e7")
    
    # Initialize OpenAI client with DeepSeek base URL
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    
    # Get prompt from command line or use default
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("Enter your prompt: ")
    
    print("\nSending request to DeepSeek API...")
    
    try:
        # Make the API request
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        
        # Print the formatted response
        print("\n" + "="*80)
        print("GENERATED TEXT FROM DEEPSEEK:")
        print("-"*80)
        print(response.choices[0].message.content)
        print("-"*80)
        print(f"Generated {len(response.choices[0].message.content)} characters")
        print("="*80 + "\n")
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {e}")
        return None

if __name__ == "__main__":
    test_deepseek() 