#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main entry point for content generation system.
Orchestrates the entire workflow from user input to final video output.
"""

import os
import sys
import json
import logging

# Add the parent directory to the path so Python can find modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.input.user_input import get_user_input
from src.input.label_manager import process_label_selection
from src.input.prompt_parser import process_custom_prompt
from src.ai.model_connector import get_ai_model
from src.ai.text_generator import generate_text
from src.ai.semantic_matcher import match_videos
from src.video.video_processor import process_videos
from src.video.hypnotic_effects import apply_hypnotic_effects
from src.audio.speech_synthesis import generate_speech
from src.subtitles.subtitle_generator import generate_subtitles
from src.composition.final_composer import compose_final_video
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

def load_config(config_path):
    """Load configuration from JSON file."""
    # Adjust path to look in code/config instead of just config
    actual_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', os.path.basename(config_path))
    try:
        with open(actual_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to the original path in case the file structure changes
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

def main():
    """Main workflow function."""
    logger.info("Starting content generation system")
    
    # Load configurations
    app_config = load_config('config/app_settings.json')
    models_config = load_config('config/models.json')
    video_categories = load_config('config/video_categories.json')
    
    # Get user input
    input_type, input_content = get_user_input()
    
    # Process based on input type
    if input_type == "label":
        # Label-based workflow
        selected_labels = process_label_selection(input_content, video_categories)
        video_files = process_videos(selected_labels)
        similarity_scores = match_videos(input_content, video_files)
        selected_videos = [v for v, s in similarity_scores if s > app_config['similarity_threshold']]
        hypnotic_videos = apply_hypnotic_effects(selected_videos)
        
    elif input_type == "prompt":
        # Free-form prompt workflow
        processed_prompt = process_custom_prompt(input_content)
        
        # Get AI model based on config
        ai_model = get_ai_model(models_config['default_model'])
        
        # Generate text content
        text_content = generate_text(ai_model, processed_prompt, 
                                      max_length=models_config['max_text_length'])
        
        print(text_content)
        # Generate speech from text
        audio_file = generate_speech(text_content)
        
        # Generate subtitles
        subtitle_file = generate_subtitles(text_content)
        
        # Match videos based on semantic similarity
        video_files = process_videos(None)  # Get all videos
        similarity_scores = match_videos(processed_prompt, video_files)
        selected_videos = [v for v, s in similarity_scores if s > app_config['similarity_threshold']]
        hypnotic_videos = apply_hypnotic_effects(selected_videos)
        
        # Compose final video
        output_path = os.path.join('data', 'output', f"generated_video_{os.getpid()}.mp4")
        compose_final_video(hypnotic_videos, audio_file, subtitle_file, output_path)
        
        logger.info(f"Video generation complete. Output saved to: {output_path}")
    
    else:
        logger.error(f"Unknown input type: {input_type}")
        return

if __name__ == "__main__":
    main() 