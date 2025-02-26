#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates speech from text using speech synthesis API.
"""

import os
import logging
import json
import requests
import tempfile

logger = logging.getLogger(__name__)

def load_speech_config():
    """
    Load speech synthesis configuration.
    
    Returns:
        dict: Speech synthesis configuration
    """
    try:
        with open('config/app_settings.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('speech_synthesis', {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading speech synthesis config: {e}")
        return {}

def generate_speech(text, output_dir=None, voice_id=None):
    """
    Generate speech from text using the configured speech synthesis API.
    
    Args:
        text (str): Text to convert to speech
        output_dir (str, optional): Directory to save audio file
        voice_id (str, optional): ID of voice to use for synthesis
    
    Returns:
        str: Path to generated audio file
    """
    if not output_dir:
        output_dir = os.path.join('data', 'output', 'audio')
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"speech_{os.getpid()}.mp3")
    
    # Load configuration
    config = load_speech_config()
    api_url = config.get('api_url')
    api_key = config.get('api_key') or os.environ.get('SPEECH_API_KEY')
    
    if not api_url or not api_key:
        logger.error("Missing speech synthesis API configuration")
        return _generate_dummy_audio(output_path)
    
    # Use provided voice ID or default from config
    voice_id = voice_id or config.get('default_voice_id', 'en_male_1')
    
    # Prepare chunks for processing (to handle API limits)
    chunks = _prepare_text_chunks(text, max_chars=3000)
    
    temp_files = []
    try:
        # Process each chunk
        for i, chunk in enumerate(chunks):
            chunk_file = os.path.join(tempfile.gettempdir(), f"speech_chunk_{i}_{os.getpid()}.mp3")
            
            # Call TTS API
            response = requests.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "text": chunk,
                    "voice_id": voice_id,
                    "output_format": "mp3",
                    "speed": 1.0,
                    "pitch": 1.0
                }
            )
            
            if response.status_code == 200:
                # Save audio chunk
                with open(chunk_file, 'wb') as f:
                    f.write(response.content)
                temp_files.append(chunk_file)
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
        
        # Combine chunks if multiple
        if len(temp_files) > 1:
            _combine_audio_files(temp_files, output_path)
        elif temp_files:
            # Copy single file to output path
            with open(temp_files[0], 'rb') as src, open(output_path, 'wb') as dst:
                dst.write(src.read())
        else:
            return _generate_dummy_audio(output_path)
        
        logger.info(f"Generated speech audio saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        return _generate_dummy_audio(output_path)
    finally:
        # Clean up temp files
        for file in temp_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except:
                pass

def _prepare_text_chunks(text, max_chars=3000):
    """
    Split text into chunks for processing.
    
    Args:
        text (str): Text to split
        max_chars (int): Maximum characters per chunk
    
    Returns:
        list: List of text chunks
    """
    chunks = []
    sentences = text.replace('\n', ' ').split('. ')
    
    current_chunk = ""
    for sentence in sentences:
        # Add period back to sentence
        if not sentence.endswith('.'):
            sentence += '.'
        
        # Check if adding this sentence would exceed the limit
        if len(current_chunk) + len(sentence) + 1 > max_chars:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk += ' ' + sentence if current_chunk else sentence
    
    # Add the last chunk if not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def _combine_audio_files(input_files, output_file):
    """
    Combine multiple audio files into one.
    
    Args:
        input_files (list): List of input audio file paths
        output_file (str): Output audio file path
    """
    try:
        # Use FFmpeg to concatenate files
        input_args = '|'.join(input_files)
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', 
            f"concat:{input_args}", 
            '-acodec', 'copy', 
            output_file
        ]
        
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        logger.error(f"Error combining audio files: {e}")
        # If combining fails, copy the first file as output
        if input_files:
            with open(input_files[0], 'rb') as src, open(output_file, 'wb') as dst:
                dst.write(src.read())

def _generate_dummy_audio(output_path):
    """
    Generate a silent audio file as fallback.
    
    Args:
        output_path (str): Path to save dummy audio
    
    Returns:
        str: Path to generated audio file
    """
    try:
        # Create 10 seconds of silence
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', 
            '-i', 'anullsrc=r=44100:cl=stereo', 
            '-t', '10', 
            output_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logger.warning(f"Generated dummy audio at {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating dummy audio: {e}")
        # Create empty file
        with open(output_path, 'wb') as f:
            pass
        return output_path 