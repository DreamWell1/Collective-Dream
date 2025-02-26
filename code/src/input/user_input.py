#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Handles user input processing for the content generation system.
"""

import logging
from src.input.label_manager import get_available_labels

logger = logging.getLogger(__name__)

def get_user_input():
    """
    Get input from the user, determining whether it's a label selection
    or free-form prompt.
    
    Returns:
        tuple: (input_type, input_content)
            - input_type: "label" or "prompt"
            - input_content: selected labels or prompt text
    """
    print("Content Generation System")
    print("========================")
    print("1. Select from predefined labels")
    print("2. Enter custom prompt")
    
    choice = input("Select an option (1/2): ")
    
    if choice == "1":
        available_labels = get_available_labels()
        print("\nAvailable Labels:")
        for i, label in enumerate(available_labels, 1):
            print(f"{i}. {label}")
        
        selected_indices = input("\nEnter the numbers of labels you want to use (comma-separated): ")
        try:
            indices = [int(idx.strip()) - 1 for idx in selected_indices.split(",")]
            selected_labels = [available_labels[idx] for idx in indices if 0 <= idx < len(available_labels)]
            return "label", selected_labels
        except (ValueError, IndexError):
            logger.error("Invalid label selection")
            return get_user_input()
    
    elif choice == "2":
        prompt = input("\nEnter your custom prompt: ")
        if not prompt.strip():
            logger.error("Empty prompt")
            return get_user_input()
        return "prompt", prompt
    
    else:
        logger.error(f"Invalid choice: {choice}")
        return get_user_input() 