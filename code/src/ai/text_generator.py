#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates text content using AI models.
"""

import logging
import os
import json
import sys

logger = logging.getLogger(__name__)

# Modified dotenv loading with error handling
try:
    from dotenv import load_dotenv
    # Try to load with explicit encoding parameter
    try:
        load_dotenv(encoding="utf-8")
    except UnicodeDecodeError:
        # If that fails, set the API key directly
        logger.warning("Could not decode .env file - it may have incorrect encoding")
        # Directly set the API key in environment
        os.environ["DEEPSEEK_API_KEY"] = "sk-7dff725207d44c71b12374519af394e7"
        logger.info("DeepSeek API key set directly in code")
except ImportError:
    logger.warning("python-dotenv not installed. Environment variables must be set manually.")

def generate_text(ai_model, prompt, max_length=8000, save_output=True, print_to_terminal=True):
    """
    Generate text content using the specified AI model.
    
    Args:
        ai_model: AI model instance
        prompt (str): The processed user prompt
        max_length (int): Maximum character length for generated text
        save_output (bool): Whether to save the generated text to file
        print_to_terminal (bool): Whether to print the generated text to terminal
    
    Returns:
        str: Generated text content
    """
    logger.info(f"Generating text with {ai_model.model_name} model")
    
    # Calculate approximate tokens based on characters
    # (rough estimate: 1 token ≈ 4 characters for English text)
    max_tokens = max(1000, int(max_length / 4))
    
    # Create a more detailed prompt for better results
    enhanced_prompt = f"""
    Based on the following topic, generate a comprehensive and engaging text 
    of approximately {max_length} characters. The content should be 
    well-structured, informative, and suitable for narration in a video:
    
    {prompt}
    
    The text should include:
    - A compelling introduction
    - Detailed exploration of the topic
    - Interesting facts or insights
    - A meaningful conclusion
    
    Please ensure the content is factually accurate and engaging.
    """
    
    # Generate text using the model
    print("\nSending prompt to AI model. Please wait...\n")
    generated_text = ai_model.generate(
        enhanced_prompt,
        max_tokens=max_tokens,
        temperature=0.7
    )
    
    # Immediately display the result in the terminal
    print("\n" + "="*80)
    print("GENERATED TEXT FROM DEEPSEEK:")
    print("-"*80)
    print(generated_text)
    print("-"*80)
    print(f"Generated {len(generated_text)} characters")
    print("="*80 + "\n")
    
    if not generated_text:
        logger.error("Failed to generate text")
        return "Error generating content. Please try again with a different prompt."
    
    # Truncate to max_length if necessary
    if len(generated_text) > max_length:
        logger.info(f"Truncating generated text from {len(generated_text)} to {max_length} characters")
        generated_text = generated_text[:max_length]
    
    # Save output if requested
    if save_output:
        output_dir = os.path.join('data', 'user_prompts')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"generated_text_{os.getpid()}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(generated_text)
        
        logger.info(f"Generated text saved to {output_file}")
    
    return generated_text 