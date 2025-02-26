#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Connector for DeepSeek API using OpenAI client.
"""

import os
import logging
import tempfile
import random
import time
import json

# Import OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI package not found. Install using: pip install openai")

logger = logging.getLogger(__name__)

class DeepseekConnector:
    """Connector for DeepSeek API using OpenAI client."""
    
    def __init__(self, config=None):
        """
        Initialize DeepSeek connector.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.config = config or {}
        
        # Add the required model_name attribute
        self.model_name = config.get("name", "DeepSeek") if config else "DeepSeek"
        
        # Check if OpenAI is available
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI package not installed. Cannot use DeepSeek connector.")
            logger.info("Will use mock responses instead.")
            self.dev_mode = True
            return
        
        if not self.api_key:
            logger.warning("No API key provided for DeepSeek. Set DEEPSEEK_API_KEY environment variable.")
            logger.info("Will use mock responses instead.")
            self.dev_mode = True
        else:
            # Initialize OpenAI client with DeepSeek base URL
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com"
                )
                self.dev_mode = False
                logger.info("DeepSeek connector initialized with OpenAI client")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.dev_mode = True
    
    def generate(self, prompt, max_tokens=2000, temperature=0.7):
        """
        Generate text using DeepSeek API.
        
        Args:
            prompt (str): Input prompt
            max_tokens (int, optional): Maximum tokens to generate
            temperature (float, optional): Sampling temperature
        
        Returns:
            str: Generated text
        """
        logger.info(f"Generating text with {self.model_name}. Prompt length: {len(prompt)}")
        
        if self.dev_mode:
            # In dev mode, use a mock response
            return self._generate_mock_response(prompt)
        
        try:
            # Make the API request using OpenAI client
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
            
            # Extract the generated text
            generated_text = response.choices[0].message.content
            
            # Print to terminal with formatting
            print("\n" + "="*80)
            print("GENERATED TEXT FROM DEEPSEEK:")
            print("-"*80)
            print(generated_text)
            print("-"*80)
            print(f"Generated {len(generated_text)} characters")
            print("="*80 + "\n")
            
            return generated_text
            
        except Exception as e:
            error_msg = f"Error generating text with DeepSeek: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _generate_mock_response(self, prompt):
        """Generate a mock response for development mode."""
        # Simulate API delay
        time.sleep(1)
        
        mock_response = """
        This is a mock response from DeepSeek API for development mode.
        
        Your prompt was: "{prompt}"
        
        In a real deployment with a valid API key, this would connect to the 
        DeepSeek API and return an actual generated response. For now, this
        placeholder text is shown instead.
        
        To use the actual DeepSeek API, please set the DEEPSEEK_API_KEY
        environment variable with your API key.
        """.format(prompt=prompt)
        
        # Print to terminal
        print("\n" + "="*80)
        print("MOCK DEEPSEEK RESPONSE (NO API KEY):")
        print("-"*80)
        print(mock_response)
        print("-"*80)
        print(f"Generated {len(mock_response)} characters")
        print("="*80 + "\n")
        
        return mock_response
    
    def generate_speech(self, text, voice="en_female_1", format="mp3"):
        """
        Generate speech using DeepSeek TTS API (if available).
        
        Args:
            text (str): Text to convert to speech
            voice (str, optional): Voice ID
            format (str, optional): Audio format
        
        Returns:
            str: Path to audio file or None
        """
        logger.info(f"Note: DeepSeek connector does not support text-to-speech yet")
        logger.info(f"Creating a mock audio file instead")
        
        # Create a mock audio file
        temp_path = os.path.join(tempfile.gettempdir(), f"mock_audio_{random.randint(1000, 9999)}.mp3")
        
        try:
            # Create an empty file
            with open(temp_path, 'wb') as f:
                # Write some random bytes to simulate an audio file
                f.write(b'\x00' * 1024)
            
            logger.info(f"Created mock audio file: {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"Error creating mock audio file: {e}")
            return None


# Test function for direct use
def test_deepseek():
    """Run a test of the DeepSeek connector."""
    connector = DeepseekConnector()
    prompt = input("Enter prompt for DeepSeek: ")
    result = connector.generate(prompt)
    return result

# Allow running directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_deepseek() 