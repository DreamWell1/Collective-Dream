#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gemini API connector for text generation.
"""

import requests
import json
import logging
import os
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# API configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your-gemini-api-key")  # Replace with your actual key
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-2.0-flash"  # Using latest Gemini 2.0 Flash model

# Model mapping to handle various model name inputs
MODEL_MAPPING = {
    "gemini": DEFAULT_MODEL,
    "gemini-pro": "gemini-pro",
    "gemini-pro-vision": "gemini-pro-vision",
    "gemini-2.0-flash": "gemini-2.0-flash",
    "gemini-2.0-pro": "gemini-2.0-pro",
}

def initialize(api_key=None, model=None):
    """Initialize the Gemini connector with API key and model."""
    global GEMINI_API_KEY, DEFAULT_MODEL
    
    if api_key:
        GEMINI_API_KEY = api_key
        logger.info("Gemini API key set manually")
    
    if model:
        if model in MODEL_MAPPING:
            DEFAULT_MODEL = MODEL_MAPPING[model]
        else:
            DEFAULT_MODEL = model
        logger.info(f"Gemini default model set to: {DEFAULT_MODEL}")
    
    logger.info(f"Gemini connector initialized with model: {DEFAULT_MODEL}")
    return True

def generate_text(model_name: str, prompt: str, max_length=1000, temperature=0.7, history=None, **kwargs):
    """Generate text using Google Gemini API directly matching the curl example"""
    try:
        # Map model name if needed
        if model_name in MODEL_MAPPING:
            actual_model = MODEL_MAPPING[model_name]
        else:
            actual_model = model_name
        
        logger.info(f"Generating text with Gemini model: {actual_model}")
        
        # Construct the API endpoint
        api_url = f"{BASE_URL}/{actual_model}:generateContent?key={GEMINI_API_KEY}"
        
        # Prepare the request headers
        headers = {
            "Content-Type": "application/json",
        }
        
        # Prepare the request body based on whether history is provided
        if history:
            # Format history into the required structure
            contents = []
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                contents.append({
                    "role": "user" if role == "user" else "model",
                    "parts": [{"text": content}]
                })
            
            # Add the current prompt as the final user message
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })
        else:
            # Simple prompt without history
            contents = [{
                "parts": [{"text": prompt}]
            }]
        
        # Generation parameters
        generation_config = {
            "temperature": temperature,
            "maxOutputTokens": max_length,
            "topP": 0.95,
            "topK": 40,
        }
        
        # Update config with any provided kwargs
        generation_config.update({k: v for k, v in kwargs.items() if k in 
                                ["temperature", "maxOutputTokens", "topP", "topK"]})
        
        # Construct the full request payload
        payload = {
            "contents": contents,
            "generationConfig": generation_config,
        }
        
        # Make the API request
        logger.debug(f"Sending request to Gemini API: {api_url}")
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract the generated text from the response
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if parts and "text" in parts[0]:
                        generated_text = parts[0]["text"]
                        logger.info(f"Successfully generated text with Gemini ({len(generated_text)} chars)")
                        return generated_text
            
            logger.warning(f"Unexpected Gemini API response structure: {json.dumps(response_data)[:200]}...")
            return f"Received response but couldn't extract text. Raw response structure unexpected."
        else:
            error_msg = f"Gemini API error: {response.status_code} - {response.text[:200]}..."
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    except Exception as e:
        error_msg = f"Gemini text generation failed: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.debug(traceback.format_exc())
        return f"Error: {error_msg}"

# For testing the connector directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test initialization
    initialize()
    
    # Test text generation
    result = generate_text(DEFAULT_MODEL, "Explain how AI works")
    print("\nGENERATED TEXT:")
    print(result) 