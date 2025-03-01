#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Text generation module for Collective Dream.
Uses Doubao API for text generation.
"""

import os
import sys
import logging
import json
import time
import requests
import socket
from typing import Dict, List, Any, Optional
from pathlib import Path
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API configuration with fallback endpoints
DOUBAO_API_KEY = "c982a865-4ee7-494e-b125-87557b53e0ee"
os.environ["DOUBAO_API_KEY"] = DOUBAO_API_KEY
logger.info("Using provided Doubao API key")

# Primary and fallback endpoints
PRIMARY_API_URL = "https://api.doubao.com/chat/completions"
FALLBACK_API_URL = "https://api.llama.biz/v1/chat/completions"  # Alternate endpoint

DEFAULT_MODEL = "doubao-llama3-8b"  # Default Doubao model

# Model mapping to handle various model name inputs
MODEL_MAPPING = {
    "doubao": DEFAULT_MODEL,
    "llama3": "doubao-llama3-8b",
    "qwen": "doubao-qwen-7b",
    "deepseek": DEFAULT_MODEL,  # Map DeepSeek requests to Doubao
    # Add other models as needed
}

def check_connectivity(domain):
    """Check if a domain is reachable"""
    try:
        # Try to resolve the domain to check DNS
        logger.info(f"Checking if domain '{domain}' is reachable...")
        domain_name = domain.replace("https://", "").replace("http://", "").split("/")[0]
        ip_address = socket.gethostbyname(domain_name)
        logger.info(f"Successfully resolved {domain_name} to {ip_address}")
        
        # Try to establish a connection
        port = 443 if domain.startswith("https") else 80
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip_address, port))
        sock.close()
        
        if result == 0:
            logger.info(f"Successfully connected to {domain_name}:{port}")
            return True
        else:
            logger.warning(f"Could not connect to {domain_name}:{port}, error code: {result}")
            return False
    except socket.gaierror:
        logger.warning(f"Could not resolve domain name: {domain_name}")
        return False
    except Exception as e:
        logger.warning(f"Connection check failed: {str(e)}")
        return False

def _get_api_key():
    """Get API key"""
    global _api_key
    
    # Use our direct key
    if DOUBAO_API_KEY:
        logger.info("Using directly configured API key")
        return DOUBAO_API_KEY
        
    # Try environment variable as backup
    api_key = os.environ.get("DOUBAO_API_KEY")
    if api_key:
        logger.info("Found Doubao API key in environment variables")
        return api_key
    
    logger.error("No API key available")
    return None

def _try_fallback_local_model(prompt, max_length=1000, temperature=0.7):
    """Try to use a local model as last resort"""
    try:
        logger.info("Attempting to use local model as fallback...")
        
        # Try to import transformers for local model inference
        try:
            from transformers import pipeline
            logger.info("Successfully imported transformers library")
            
            # Try to use a small local model
            generator = pipeline('text-generation', model='gpt2')
            result = generator(prompt, max_length=max_length, temperature=temperature)[0]['generated_text']
            
            logger.info("Successfully generated text using local model")
            return "⚠️ [USING LOCAL MODEL DUE TO API CONNECTION FAILURE]\n\n" + result
        except ImportError:
            logger.warning("Transformers library not available for local model fallback")
            return None
    except Exception as e:
        logger.warning(f"Local model fallback failed: {str(e)}")
        return None

def generate_text(ai_model, prompt: str, max_length: int = 1000, 
                  temperature: float = 0.7, history: List[Dict] = None) -> str:
    """
    Generate text using Doubao API with fallback options.
    
    Args:
        ai_model: The model to use (string) or model connector object
        prompt: The prompt text for generation
        max_length: Maximum tokens to generate
        temperature: Temperature parameter (0.0-1.0)
        history: Optional conversation history
        
    Returns:
        Generated text string
    """
    # Get API key
    api_key = _get_api_key()
    if not api_key:
        return "ERROR: No API key available. Please provide a valid API key."
    
    # Determine which model to use
    if isinstance(ai_model, str):
        # It's a string, use the mapping
        ai_model_str = ai_model.lower()
        if ai_model_str in MODEL_MAPPING:
            model_name = MODEL_MAPPING[ai_model_str]
            logger.info(f"Mapped model '{ai_model}' to Doubao model '{model_name}'")
        else:
            # If unknown, use default
            model_name = DEFAULT_MODEL
            logger.warning(f"Unknown model name: '{ai_model}', using default '{model_name}'")
    else:
        # It's an object, try to use it directly first
        try:
            if hasattr(ai_model, 'generate'):
                logger.info(f"Using model object's generate method")
                return ai_model.generate(prompt, max_length, temperature, history)
            
            # Try to infer the model name from the object type
            model_class_name = ai_model.__class__.__name__
            logger.info(f"Received model object of type: {model_class_name}")
            
            # Default to standard model
            model_name = DEFAULT_MODEL
            logger.info(f"Using default Doubao model: {model_name}")
        except Exception as e:
            logger.warning(f"Error using model object directly: {e}")
            model_name = DEFAULT_MODEL
            logger.info(f"Falling back to default model: {model_name}")
    
    # Check connectivity to the primary API endpoint
    primary_reachable = check_connectivity(PRIMARY_API_URL)
    if not primary_reachable:
        logger.warning(f"Primary API endpoint is not reachable: {PRIMARY_API_URL}")
        # Check fallback endpoint
        fallback_reachable = check_connectivity(FALLBACK_API_URL)
        if fallback_reachable:
            logger.info(f"Using fallback API endpoint: {FALLBACK_API_URL}")
            api_url = FALLBACK_API_URL
        else:
            logger.error("Both primary and fallback API endpoints are unreachable")
            
            # Try local model as last resort
            local_result = _try_fallback_local_model(prompt, max_length, temperature)
            if local_result:
                return local_result
                
            # Simple offline text generation as absolute last resort
            logger.error("No API endpoints are reachable and local model fallback failed")
            return f"""
⚠️ OFFLINE MODE - NETWORK CONNECTIVITY ISSUE

I couldn't connect to any text generation API endpoints. Here are the issues:

1. Primary endpoint ({PRIMARY_API_URL}) is unreachable
2. Fallback endpoint is also unreachable
3. Local model fallback was not available

Your prompt was:
---
{prompt}
---

Please check your internet connection and try again later, or configure a local text generation model.
"""
    else:
        api_url = PRIMARY_API_URL
    
    # Make the API request
    try:
        logger.info(f"Generating text with Doubao ({model_name}), prompt length: {len(prompt)}")
        start_time = time.time()
        
        # Prepare messages
        messages = []
        
        # Add history if provided
        if history:
            messages.extend(history)
        
        # Add the current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": max_length,
            "temperature": temperature
        }
        
        # Log request details for debugging
        logger.info(f"Sending request to API: {api_url}")
        logger.info(f"Using model: {model_name}")
        
        # Make API request
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        # Check for HTTP errors
        if response.status_code != 200:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            return f"Error: API request failed with status code {response.status_code}. Response: {response.text}"
        
        # Parse response
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0 and "message" in result["choices"][0]:
            generated_text = result["choices"][0]["message"]["content"]
            
            elapsed_time = time.time() - start_time
            logger.info(f"Generated {len(generated_text)} characters in {elapsed_time:.2f} seconds")
            
            return generated_text
        else:
            logger.error(f"Unexpected response structure: {result}")
            return "Error: Unexpected response from API"
            
    except requests.RequestException as e:
        logger.error(f"Request to API failed: {str(e)}")
        
        # If the error is due to network connectivity, try a basic offline mode
        if "Failed to resolve" in str(e) or "getaddrinfo failed" in str(e):
            local_result = _try_fallback_local_model(prompt, max_length, temperature)
            if local_result:
                return local_result
            
            return f"""
⚠️ NETWORK CONNECTIVITY ISSUE

I couldn't connect to the text generation API due to a network error.
The specific error was:

{str(e)}

Your prompt was:
---
{prompt}
---

Please check your internet connection or try one of these solutions:
1. Make sure you're connected to the internet
2. Check if you need to configure a proxy server
3. Verify that api.doubao.com is reachable from your network
4. Try using a different API endpoint or a local model
"""
        
        return f"Error connecting to API: {str(e)}"
    except Exception as e:
        logger.error(f"Text generation failed: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Error generating text: {str(e)}"

def set_model(model_name: str) -> bool:
    """Set the default model to use"""
    global DEFAULT_MODEL
    
    if model_name in MODEL_MAPPING:
        DEFAULT_MODEL = MODEL_MAPPING[model_name]
        logger.info(f"Default model set to {DEFAULT_MODEL}")
        return True
    else:
        # Accept any model name
        DEFAULT_MODEL = model_name
        logger.warning(f"Setting default model to unverified name: {model_name}")
        return True

def perform_network_diagnostics():
    """Perform basic network diagnostics and return results"""
    diagnostics = []
    
    # Check DNS resolution
    domains_to_check = [
        "api.doubao.com",
        "api.llama.biz",
        "google.com",  # Reference check
        "openai.com",  # Reference check
    ]
    
    diagnostics.append("=== DNS Resolution Tests ===")
    for domain in domains_to_check:
        try:
            ip = socket.gethostbyname(domain)
            diagnostics.append(f"✅ {domain} → {ip}")
        except socket.gaierror:
            diagnostics.append(f"❌ {domain} → Failed to resolve")
    
    # Check if we have internet connectivity at all
    diagnostics.append("\n=== Internet Connectivity ===")
    reference_sites = ["google.com", "microsoft.com", "cloudflare.com"]
    
    for site in reference_sites:
        try:
            ip = socket.gethostbyname(site)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((ip, 443))
            s.close()
            if result == 0:
                diagnostics.append(f"✅ Connection to {site} (port 443) succeeded")
            else:
                diagnostics.append(f"❌ Connection to {site} (port 443) failed with code {result}")
        except Exception as e:
            diagnostics.append(f"❌ Connection to {site} failed: {str(e)}")
    
    return "\n".join(diagnostics)

# For testing
if __name__ == "__main__":
    print("\nTesting text generation with API...")
    
    # Check if API key is available
    api_key = _get_api_key()
    if not api_key:
        print("❌ No API key found.")
        sys.exit(1)
    else:
        print(f"✅ Using API key: {api_key[:5]}...{api_key[-5:]}")
    
    # Run network diagnostics
    print("\n=== NETWORK DIAGNOSTICS ===")
    diagnostics = perform_network_diagnostics()
    print(diagnostics)
    
    # Get prompt from command line or use default
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Write a short poem about artificial intelligence in Chinese"
    
    print(f"\nGenerating text with prompt: {prompt}")
    
    result = generate_text(DEFAULT_MODEL, prompt)
    print("\nGENERATED TEXT:")
    print(result) 