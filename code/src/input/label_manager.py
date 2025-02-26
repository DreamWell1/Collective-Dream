#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Manages predefined label selection for content generation.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

def get_available_labels():
    """
    Get all available labels from video categories configuration.
    
    Returns:
        list: List of available label names
    """
    try:
        with open('config/video_categories.json', 'r', encoding='utf-8') as f:
            categories = json.load(f)
        return [category["name"] for category in categories]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading labels: {e}")
        return []

def process_label_selection(selected_labels, video_categories):
    """
    Process the selected labels to retrieve associated video categories.
    
    Args:
        selected_labels (list): List of selected label names
        video_categories (dict): Dictionary containing video categories configuration
    
    Returns:
        list: Processed label data with associated metadata
    """
    processed_labels = []
    
    for label in selected_labels:
        for category in video_categories:
            if category["name"] == label:
                processed_labels.append({
                    "name": label,
                    "id": category.get("id"),
                    "path": category.get("video_path"),
                    "keywords": category.get("keywords", [])
                })
                break
    
    logger.info(f"Processed labels: {[label['name'] for label in processed_labels]}")
    return processed_labels 