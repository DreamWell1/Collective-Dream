#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Text generator that prefers Gemini but falls back to other models if needed.
"""

import os
import sys
import json
import requests
import logging
from pathlib import Path
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gemini API configuration
GEMINI_API_KEY = os.environ.get("AIzaSyBetNtlG5HUUJAliODKEQQWuN8UtkhLxk8", "AIzaSyBetNtlG5HUUJAliODKEQQWuN8UtkhLxk8")  # Replace with your actual key
GEMINI_MODEL = "gemini-2.0-flash"  # Default Gemini model

# Doubao API configuration (as fallback)
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "")
DOUBAO_API_URL = "https://api.doubao.com/chat/completions"
DOUBAO_MODEL = "doubao-llama3-8b"  # Default Doubao model

# Base URLs
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

def generate_with_gemini(prompt, model=GEMINI_MODEL, max_length=1000, temperature=0.7, history=None):
    """Generate text using Gemini API."""
    try:
        # Check if API key is available
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key":
            logger.warning("Gemini API key not set, skipping Gemini")
            return None, "Gemini API key not configured"
        
        logger.info(f"Attempting generation with Gemini model: {model}")
        
        # Construct the API endpoint
        api_url = f"{GEMINI_BASE_URL}/{model}:generateContent?key={GEMINI_API_KEY}"
        
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
        
        # Construct the full request payload
        payload = {
            "contents": contents,
            "generationConfig": generation_config,
        }
        
        # Make the API request
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract the generated text from the response
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if parts and "text" in parts[0]:
                        result = parts[0]["text"]
                        logger.info(f"Successfully generated {len(result)} characters with Gemini")
                        return result, None
            
            return None, f"Unexpected Gemini API response structure"
        else:
            return None, f"Gemini API error: {response.status_code} - {response.text}"
    
    except Exception as e:
        logger.error(f"Error with Gemini: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None, f"Gemini error: {str(e)}"

def generate_with_doubao(prompt, model=DOUBAO_MODEL, max_length=1000, temperature=0.7, history=None):
    """Generate text using Doubao API as fallback."""
    try:
        # Check if API key is available
        if not DOUBAO_API_KEY:
            logger.warning("Doubao API key not set, using mock mode")
            return f"[MOCK] Response for: {prompt}", None
        
        logger.info(f"Falling back to Doubao model: {model}")
        
        # Prepare the request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DOUBAO_API_KEY}"
        }
        
        # Prepare messages from history if provided
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        
        # Prepare the request payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_length,
            "temperature": temperature
        }
        
        # Make the API request
        response = requests.post(DOUBAO_API_URL, headers=headers, json=payload, timeout=30)
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                result = response_data["choices"][0]["message"]["content"]
                logger.info(f"Successfully generated {len(result)} characters with Doubao")
                return result, None
            
            return None, "Unexpected Doubao API response structure"
        else:
            return None, f"Doubao API error: {response.status_code} - {response.text}"
    
    except Exception as e:
        logger.error(f"Error with Doubao: {str(e)}")
        return None, f"Doubao error: {str(e)}"

# Add a new function to transform prompts into first-person narratives
def transform_to_narrative_prompt(original_prompt):
    """
    Transform a basic prompt into a first-person narrative request.
    """
    narrative_prefix = "Write a first-person narrative story where I am the main character. Use vivid descriptions and engaging dialogue. The story should be about: "
    
    # Clean the original prompt to avoid redundancy
    cleaned_prompt = original_prompt
    if "write" in cleaned_prompt.lower() or "story" in cleaned_prompt.lower():
        # If it already includes instructions about writing a story, extract the core topic
        import re
        topic_match = re.search(r"(?:about|where|with|involving)(.*)", cleaned_prompt, re.IGNORECASE)
        if topic_match:
            cleaned_prompt = topic_match.group(1).strip()
    
    # Construct the narrative prompt
    narrative_prompt = narrative_prefix + cleaned_prompt
    
    logger.info(f"Transformed prompt: '{original_prompt}' -> '{narrative_prompt}'")
    return narrative_prompt

def generate_text(model_name=None, prompt="", max_length=1000, temperature=0.7, history=None, narrative_mode=True, **kwargs):
    """
    Generate text - ALWAYS try Gemini first unless explicitly told to use Doubao.
    
    Args:
        model_name: Name of the model to use
        prompt: The input prompt
        max_length: Maximum length of generated text
        temperature: Control randomness (higher = more random)
        history: List of previous messages for context
        narrative_mode: Whether to transform prompts into first-person narratives
        **kwargs: Additional parameters
    """
    result = None
    error = None
    
    # Transform the prompt into a narrative if narrative_mode is enabled
    if narrative_mode and prompt and not history:
        original_prompt = prompt
        prompt = transform_to_narrative_prompt(original_prompt)
        logger.info(f"Using narrative mode: transformed '{original_prompt}' to '{prompt}'")
    
    # Debug info - show exactly what's being requested
    logger.info(f"TEXT GENERATION REQUEST: model_name={model_name}, prompt length={len(prompt)}")
    
    # CRITICAL CHANGE - ALWAYS TRY GEMINI FIRST, no matter what
    # Only exception is if model_name explicitly contains "doubao"
    
    # Set up which Gemini model to use
    if isinstance(model_name, str) and model_name.lower().startswith("gemini"):
        gemini_model = model_name  # Use the specified Gemini model
    else:
        gemini_model = GEMINI_MODEL  # Use default Gemini model
    
    # Check ONLY for explicit Doubao request
    explicit_doubao_request = False
    if isinstance(model_name, str) and "doubao" in model_name.lower():
        explicit_doubao_request = True
        logger.info(f"NOTE: Explicit Doubao model requested: {model_name}")
    
    # ALWAYS TRY GEMINI FIRST (unless explicit Doubao request)
    if not explicit_doubao_request:
        logger.info(f"USING GEMINI FIRST with model: {gemini_model}")
        result, error = generate_with_gemini(prompt, gemini_model, max_length, temperature, history)
        
        # Only fall back to Doubao if Gemini fails
        if result is None:
            logger.warning(f"Gemini failed: {error}, trying Doubao as fallback")
            result, fallback_error = generate_with_doubao(prompt, DOUBAO_MODEL, max_length, temperature, history)
            if result is None:
                error = f"All models failed. Gemini: {error}, Doubao: {fallback_error}"
    else:
        # Only if explicitly requested, try Doubao first
        logger.info(f"Explicitly requested Doubao model: {model_name}")
        result, error = generate_with_doubao(prompt, model_name, max_length, temperature, history)
        
        # If Doubao fails, try Gemini as fallback
        if result is None:
            logger.warning(f"Doubao failed: {error}, trying Gemini as fallback")
            result, fallback_error = generate_with_gemini(prompt, GEMINI_MODEL, max_length, temperature, history)
            if result is None:
                error = f"All models failed. Doubao: {error}, Gemini: {fallback_error}"
    
    # Return the result or error message
    if result is not None:
        return result
    else:
        logger.error(f"Text generation failed: {error}")
        return f"Error: {error}"

# Direct execution from command line
if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="Generate text using AI models")
    parser.add_argument("prompt", nargs="*", help="The prompt to generate text from")
    parser.add_argument("--model", "-m", help="Model to use (default: Gemini)")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature (randomness)")
    parser.add_argument("--max-length", "-l", type=int, default=1000, help="Maximum output length")
    parser.add_argument("--no-narrative", action="store_true", help="Disable narrative mode")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get prompt from arguments or ask for input
    if args.prompt:
        prompt = " ".join(args.prompt)
    else:
        prompt = input("Enter your prompt: ")
    
    # Force OUTPUT showing we're using Gemini first
    print("\n===== GENERATING NARRATIVE WITH GEMINI =====")
    print(f"Prompt: {prompt}")
    print("=" * 40)
    
    # Generate text with narrative mode and print the result
    result = generate_text(
        model_name=args.model,
        prompt=prompt,
        max_length=args.max_length,
        temperature=args.temperature,
        narrative_mode=not args.no_narrative
    )
    
    print("\nGENERATED STORY:")
    print("-" * 40)
    print(result)
    print("-" * 40) 