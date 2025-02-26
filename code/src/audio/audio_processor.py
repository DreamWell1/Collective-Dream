#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Processes audio files for the content generation system.
"""

import os
import logging
import subprocess
import tempfile
from pydub import AudioSegment

logger = logging.getLogger(__name__)

def process_audio(audio_path, output_dir=None, normalize=True, remove_noise=True):
    """
    Process audio file with various enhancements.
    
    Args:
        audio_path (str): Path to audio file
        output_dir (str, optional): Directory to save processed audio
        normalize (bool): Whether to normalize audio levels
        remove_noise (bool): Whether to apply noise reduction
    
    Returns:
        str: Path to processed audio file
    """
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return None
    
    if not output_dir:
        output_dir = os.path.join('data', 'output', 'processed_audio')
    
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(audio_path)
    output_path = os.path.join(output_dir, f"processed_{filename}")
    
    try:
        if normalize or remove_noise:
            # Use FFmpeg for audio processing
            ffmpeg_cmd = ['ffmpeg', '-y', '-i', audio_path]
            
            filter_chain = []
            if normalize:
                # Add normalization filter
                filter_chain.append("loudnorm=I=-16:TP=-1.5:LRA=11")
            
            if remove_noise:
                # Add noise reduction filter
                filter_chain.append("afftdn=nf=-25")
            
            if filter_chain:
                ffmpeg_cmd.extend(['-af', ','.join(filter_chain)])
            
            # Add output format settings
            ffmpeg_cmd.extend(['-ar', '44100', '-ac', '2', output_path])
            
            # Run FFmpeg process
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info(f"Processed audio saved to {output_path}")
            return output_path
        else:
            # If no processing needed, just copy the file
            with open(audio_path, 'rb') as src, open(output_path, 'wb') as dst:
                dst.write(src.read())
            return output_path
    
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return audio_path  # Return original path on error

def adjust_audio_duration(audio_path, target_duration, output_dir=None):
    """
    Adjust audio duration to match target length.
    
    Args:
        audio_path (str): Path to audio file
        target_duration (float): Target duration in seconds
        output_dir (str, optional): Directory to save adjusted audio
    
    Returns:
        str: Path to adjusted audio file
    """
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return None
    
    if not output_dir:
        output_dir = os.path.join('data', 'output', 'processed_audio')
    
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(audio_path)
    output_path = os.path.join(output_dir, f"adjusted_{filename}")
    
    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_path)
        current_duration = len(audio) / 1000.0  # Convert ms to seconds
        
        if abs(current_duration - target_duration) < 0.5:
            # Already close enough to target duration
            return audio_path
        
        if current_duration > target_duration:
            # Need to shorten audio
            logger.info(f"Shortening audio from {current_duration:.2f}s to {target_duration:.2f}s")
            ratio = target_duration / current_duration
            
            # Use FFmpeg atempo filter (limited to 0.5-2.0 range)
            if 0.5 <= ratio <= 2.0:
                subprocess.run([
                    'ffmpeg', '-y', '-i', audio_path,
                    '-filter:a', f'atempo={ratio}',
                    output_path
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                # For extreme ratios, use multiple passes or other approach
                temp_path = tempfile.mktemp(suffix='.mp3')
                
                if ratio < 0.5:
                    # Multiple passes for extreme speedup
                    first_ratio = 0.5
                    second_ratio = ratio / 0.5
                    
                    subprocess.run([
                        'ffmpeg', '-y', '-i', audio_path,
                        '-filter:a', f'atempo={first_ratio}',
                        temp_path
                    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    subprocess.run([
                        'ffmpeg', '-y', '-i', temp_path,
                        '-filter:a', f'atempo={second_ratio}',
                        output_path
                    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    # For extreme slowdown, use alternative approach
                    subprocess.run([
                        'ffmpeg', '-y', '-i', audio_path,
                        '-filter:a', 'asetrate=44100*0.5,aresample=44100',
                        output_path
                    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        else:
            # Need to extend audio (loop or add silence)
            logger.info(f"Extending audio from {current_duration:.2f}s to {target_duration:.2f}s")
            
            # Add silence to the end
            silence_duration = target_duration - current_duration
            silence = AudioSegment.silent(duration=int(silence_duration * 1000))
            extended_audio = audio + silence
            
            # Export extended audio
            extended_audio.export(output_path, format="mp3")
        
        logger.info(f"Adjusted audio saved to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error adjusting audio duration: {e}")
        return audio_path  # Return original path on error

def merge_audio_tracks(audio_paths, output_path=None, crossfade=1000):
    """
    Merge multiple audio tracks into one with crossfade.
    
    Args:
        audio_paths (list): List of audio file paths
        output_path (str, optional): Path to save merged audio
        crossfade (int): Crossfade duration in milliseconds
    
    Returns:
        str: Path to merged audio file
    """
    if not audio_paths:
        logger.error("No audio paths provided for merging")
        return None
    
    if not output_path:
        output_dir = os.path.join('data', 'output', 'processed_audio')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"merged_audio_{os.getpid()}.mp3")
    
    try:
        # Check if we have only one audio file
        if len(audio_paths) == 1:
            with open(audio_paths[0], 'rb') as src, open(output_path, 'wb') as dst:
                dst.write(src.read())
            return output_path
        
        # Load the first audio file
        merged = AudioSegment.from_file(audio_paths[0])
        
        # Merge subsequent files with crossfade
        for audio_path in audio_paths[1:]:
            next_audio = AudioSegment.from_file(audio_path)
            merged = merged.append(next_audio, crossfade=crossfade)
        
        # Export merged audio
        merged.export(output_path, format="mp3")
        logger.info(f"Merged {len(audio_paths)} audio tracks to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error merging audio tracks: {e}")
        # If merging fails, return the first audio path
        return audio_paths[0] if audio_paths else None

def add_background_music(voice_path, music_path, output_path=None, music_volume=0.2):
    """
    Add background music to voice audio with volume adjustment.
    
    Args:
        voice_path (str): Path to voice audio file
        music_path (str): Path to music audio file
        output_path (str, optional): Path to save combined audio
        music_volume (float): Volume level for background music (0.0-1.0)
    
    Returns:
        str: Path to combined audio file
    """
    if not os.path.exists(voice_path) or not os.path.exists(music_path):
        logger.error(f"Audio file not found: {voice_path} or {music_path}")
        return voice_path
    
    if not output_path:
        output_dir = os.path.join('data', 'output', 'processed_audio')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"voice_with_music_{os.getpid()}.mp3")
    
    try:
        # Load audio files
        voice = AudioSegment.from_file(voice_path)
        music = AudioSegment.from_file(music_path)
        
        # Adjust music volume
        music = music - (20 - (music_volume * 20))  # Converts 0.0-1.0 to -20dB to 0dB
        
        # Loop music if it's shorter than voice
        voice_duration = len(voice)
        music_duration = len(music)
        
        if music_duration < voice_duration:
            repetitions = int(voice_duration / music_duration) + 1
            music = music * repetitions
        
        # Trim music to match voice duration
        music = music[:voice_duration]
        
        # Mix voice and music
        combined = voice.overlay(music)
        
        # Export combined audio
        combined.export(output_path, format="mp3")
        logger.info(f"Added background music to voice, saved to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding background music: {e}")
        return voice_path  # Return original voice path on error 