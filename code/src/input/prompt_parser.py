#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Processes free-form prompt inputs for content generation.
"""

import re
import logging

logger = logging.getLogger(__name__)

def process_custom_prompt(prompt_text):
    """
    Process a custom user prompt to prepare it for AI processing.
    
    Args:
        prompt_text (str): Raw user prompt text
    
    Returns:
        str: Processed prompt ready for AI model input
    """
    # Remove excessive whitespace
    processed = re.sub(r'\s+', ' ', prompt_text).strip()
    
    # Add context if prompt is too short
    if len(processed) < 10:
        logger.warning("Prompt is very short, adding context")
        processed = f"Create content about: {processed}"
    
    # Ensure the prompt ends with appropriate punctuation
    if not processed.endswith(('.', '?', '!')):
        processed += '.'
    
    logger.info(f"Processed prompt: {processed[:50]}...")
    return processed 