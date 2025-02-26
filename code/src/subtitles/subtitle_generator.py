#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates subtitle files from text content.
"""

import os
import logging
import re
import math

logger = logging.getLogger(__name__)

def generate_subtitles(text, output_dir=None, words_per_line=10, chars_per_line=50):
    """
    Generate SRT subtitle file from text content.
    
    Args:
        text (str): Text content for subtitles
        output_dir (str, optional): Directory to save subtitle file
        words_per_line (int): Maximum words per subtitle line
        chars_per_line (int): Maximum characters per subtitle line
    
    Returns:
        str: Path to generated subtitle file
    """
    if not output_dir:
        output_dir = os.path.join('data', 'output', 'subtitles')
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"subtitles_{os.getpid()}.srt")
    
    # Clean text - remove excessive whitespace and normalize punctuation
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    
    # Split text into chunks that will become subtitle entries
    subtitle_chunks = _split_text_into_chunks(cleaned_text, words_per_line, chars_per_line)
    
    # Estimate duration based on text length (approx. 15 chars per second)
    total_chars = len(cleaned_text)
    total_duration = max(5, math.ceil(total_chars / 15))  # At least 5 seconds
    chars_per_second = total_chars / total_duration
    
    # Generate SRT content
    srt_content = _generate_srt_format(subtitle_chunks, total_duration, chars_per_second)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    
    logger.info(f"Generated subtitle file: {output_path}")
    return output_path

def _split_text_into_chunks(text, words_per_line=10, chars_per_line=50):
    """
    Split text into appropriate chunks for subtitles.
    
    Args:
        text (str): Text to split
        words_per_line (int): Maximum words per line
        chars_per_line (int): Maximum characters per line
    
    Returns:
        list: List of text chunks for subtitles
    """
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = ""
    current_words = 0
    
    for sentence in sentences:
        words = sentence.split()
        
        # If sentence can fit in one chunk
        if len(sentence) <= chars_per_line and len(words) <= words_per_line:
            if current_words + len(words) <= words_per_line and len(current_chunk + " " + sentence) <= chars_per_line:
                current_chunk += " " + sentence if current_chunk else sentence
                current_words += len(words)
            else:
                # Start a new chunk
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
                current_words = len(words)
        else:
            # Need to split the sentence
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
                current_words = 0
            
            # Split long sentence into smaller chunks
            temp_chunk = ""
            temp_words = 0
            
            for word in words:
                if temp_words + 1 <= words_per_line and len(temp_chunk + " " + word) <= chars_per_line:
                    temp_chunk += " " + word if temp_chunk else word
                    temp_words += 1
                else:
                    chunks.append(temp_chunk)
                    temp_chunk = word
                    temp_words = 1
            
            if temp_chunk:
                current_chunk = temp_chunk
                current_words = temp_words
    
    # Add the last chunk if not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def _generate_srt_format(subtitle_chunks, total_duration, chars_per_second):
    """
    Generate SRT format content from text chunks.
    
    Args:
        subtitle_chunks (list): List of text chunks
        total_duration (int): Total duration in seconds
        chars_per_second (float): Characters per second rate
    
    Returns:
        str: SRT formatted content
    """
    srt_content = ""
    chunk_count = len(subtitle_chunks)
    
    # Calculate time per chunk (with some flexibility)
    time_per_chunk = total_duration / chunk_count
    
    for i, chunk in enumerate(subtitle_chunks):
        # Calculate start and end times
        chunk_duration = max(1, min(10, len(chunk) / chars_per_second))
        start_time = i * time_per_chunk
        end_time = start_time + chunk_duration
        
        # Format times as SRT format (HH:MM:SS,mmm)
        start_formatted = _format_time(start_time)
        end_formatted = _format_time(end_time)
        
        # Add subtitle entry
        srt_content += f"{i+1}\n"
        srt_content += f"{start_formatted} --> {end_formatted}\n"
        srt_content += f"{chunk}\n\n"
    
    return srt_content

def _format_time(seconds):
    """
    Format seconds into SRT time format (HH:MM:SS,mmm).
    
    Args:
        seconds (float): Time in seconds
    
    Returns:
        str: Formatted time string
    """
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"

def align_subtitles_with_audio(subtitle_path, audio_duration):
    """
    Adjust subtitle timing to match audio duration.
    
    Args:
        subtitle_path (str): Path to subtitle file
        audio_duration (float): Duration of audio in seconds
    
    Returns:
        str: Path to adjusted subtitle file
    """
    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse subtitle entries
        entries = re.split(r'\n\n+', content.strip())
        subtitle_count = len(entries)
        
        # Calculate new timing
        new_content = ""
        for i, entry in enumerate(entries):
            lines = entry.split('\n')
            if len(lines) < 3:
                continue
            
            index = lines[0]
            timing_line = lines[1]
            subtitle_text = '\n'.join(lines[2:])
            
            # Calculate new start and end times
            start_ratio = i / subtitle_count
            end_ratio = (i + 1) / subtitle_count
            
            new_start = start_ratio * audio_duration
            new_end = end_ratio * audio_duration
            
            # Format new timing
            new_start_str = _format_time(new_start)
            new_end_str = _format_time(new_end)
            
            # Create adjusted entry
            new_entry = f"{index}\n{new_start_str} --> {new_end_str}\n{subtitle_text}\n\n"
            new_content += new_entry
        
        # Write adjusted subtitles
        adjusted_path = subtitle_path.replace('.srt', '_adjusted.srt')
        with open(adjusted_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Adjusted subtitles saved to {adjusted_path}")
        return adjusted_path
    
    except Exception as e:
        logger.error(f"Error adjusting subtitles: {e}")
        return subtitle_path 