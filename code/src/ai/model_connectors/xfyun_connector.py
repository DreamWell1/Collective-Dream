#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Connector for iFlyTek Xfyun API
"""

import os
import logging
import time
import base64
import hashlib
import hmac
import json
import requests
from datetime import datetime
from urllib.parse import urlencode, quote

logger = logging.getLogger(__name__)

class XfyunConnector:
    """Connector for Xfyun natural language processing APIs."""
    
    def __init__(self, config=None):
        """
        Initialize Xfyun connector.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Get credentials from environment or config
        self.app_id = os.environ.get("XFYUN_APP_ID") or self.config.get("app_id")
        self.api_key = os.environ.get("XFYUN_API_KEY") or self.config.get("api_key")
        self.api_secret = os.environ.get("XFYUN_API_SECRET") or self.config.get("api_secret")
        
        # Add the required model_name attribute
        self.model_name = self.config.get("name", "Xfyun") if config else "Xfyun"
        
        # Sparkchat API endpoint
        self.api_url = self.config.get("api_url", "https://spark-api.xf-yun.com/v2.1/chat")
        
        if not all([self.app_id, self.api_key, self.api_secret]):
            logger.warning("Missing Xfyun credentials. Set XFYUN_APP_ID, XFYUN_API_KEY, XFYUN_API_SECRET environment variables.")
            logger.info("Will use mock responses instead.")
            self.dev_mode = True
        else:
            self.dev_mode = False
            logger.info(f"Xfyun connector initialized with endpoint: {self.api_url}")
    
    def _build_authorization_url(self):
        """
        Build the URL with the authorization parameters.
        
        Returns:
            str: The fully formed API URL with authorization parameters
        """
        # Create URL with authorization parameters
        host = self.api_url.split('://')[1].split('/')[0]
        path = '/' + '/'.join(self.api_url.split('://')[1].split('/')[1:])
        
        # Current timestamp (seconds)
        now = int(time.time())
        
        # Query parameters
        query_dict = {
            "appid": self.app_id,
            "timestamp": str(now),
            "nonce": str(now)  # You can use a more random nonce if needed
        }
        
        # Create query string
        query_str = urlencode(query_dict)
        
        # Create string to sign
        str_to_sign = "host: " + host + "\n"
        str_to_sign += "date: " + str(now) + "\n"
        str_to_sign += "GET " + path + "?" + query_str + " HTTP/1.1"
        
        # Calculate signature
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                str_to_sign.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        # Create authorization header
        authorization = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        
        # URL encode the authorization header
        authorization_encode = quote(authorization)
        
        # Construct final URL
        full_url = f"{self.api_url}?{query_str}&authorization={authorization_encode}"
        
        return full_url
    
    def generate(self, prompt, max_tokens=2000, temperature=0.7):
        """
        Generate text using Xfyun Spark API.
        
        Args:
            prompt (str): Input prompt
            max_tokens (int, optional): Maximum tokens to generate
            temperature (float, optional): Sampling temperature
            
        Returns:
            str: Generated text
        """
        logger.info(f"Generating text with {self.model_name}. Prompt length: {len(prompt)}")
        
        if self.dev_mode:
            return self._generate_mock_response(prompt)
        
        try:
            # Build the API URL with authorization
            api_url = self._build_authorization_url()
            
            # Prepare the request payload
            payload = {
                "header": {
                    "app_id": self.app_id,
                    "uid": f"user_{int(time.time())}"
                },
                "parameter": {
                    "chat": {
                        "domain": "general",
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                },
                "payload": {
                    "message": {
                        "text": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                }
            }
            
            # Make the API request
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Extract and print the response
            if result.get("header", {}).get("code") == 0:
                text_list = result.get("payload", {}).get("choices", {}).get("text", [])
                if text_list and len(text_list) > 0:
                    generated_text = text_list[0].get("content", "")
                    
                    # Print to terminal with formatting
                    print("\n" + "="*80)
                    print("XFYUN GENERATED TEXT:")
                    print("-"*80)
                    print(generated_text)
                    print("-"*80)
                    print(f"Generated {len(generated_text)} characters")
                    print("="*80 + "\n")
                    
                    return generated_text
                else:
                    logger.error("No text content in Xfyun response")
                    return "Error: No text generated by Xfyun API."
            else:
                error_code = result.get("header", {}).get("code")
                error_message = result.get("header", {}).get("message", "Unknown error")
                logger.error(f"Xfyun API error {error_code}: {error_message}")
                return f"Error {error_code}: {error_message}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making request to Xfyun API: {str(e)}"
            logger.error(error_msg)
            return error_msg
        
        except json.JSONDecodeError:
            error_msg = "Error: Failed to parse response from Xfyun API."
            logger.error(error_msg)
            return error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _generate_mock_response(self, prompt):
        """Generate a mock response for development mode."""
        # Simulate API delay
        time.sleep(1)
        
        mock_response = """
        This is a mock response from Xfyun API for development mode.
        
        Your prompt was: "{prompt}"
        
        In a real deployment with valid credentials, this would connect to the 
        Xfyun API and return an actual generated response. For now, this
        placeholder text is shown instead.
        
        To use the actual Xfyun API, please set the XFYUN_APP_ID, XFYUN_API_KEY,
        and XFYUN_API_SECRET environment variables.
        """.format(prompt=prompt)
        
        # Print to terminal
        print("\n" + "="*80)
        print("MOCK XFYUN RESPONSE (NO CREDENTIALS):")
        print("-"*80)
        print(mock_response)
        print("-"*80)
        print(f"Generated {len(mock_response)} characters")
        print("="*80 + "\n")
        
        return mock_response


# Test function for direct use
def test_xfyun():
    """Run a test of the Xfyun connector."""
    connector = XfyunConnector()
    prompt = input("Enter prompt for Xfyun: ")
    result = connector.generate(prompt)
    return result

# Allow running directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_xfyun()