#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Applies hypnotic effects to videos.
"""

import os
import logging
import subprocess
import tempfile
import random

logger = logging.getLogger(__name__)

def apply_hypnotic_effects(video_files, output_dir=None):
    """
    Apply hypnotic effects to selected videos.
    
    Args:
        video_files (list): List of video file paths
        output_dir (str, optional): Directory to save processed videos
    
    Returns:
        list: Paths to processed video files
    """
    if not video_files:
        logger.warning("No video files provided for processing")
        return []
    
    if not output_dir:
        output_dir = os.path.join('data', 'output', 'processed_videos')
    
    os.makedirs(output_dir, exist_ok=True)
    processed_videos = []
    
    for i, video_path in enumerate(video_files):
        try:
            output_path = os.path.join(output_dir, f"hypnotic_{i}_{os.path.basename(video_path)}")
            
            # Apply video effects using FFmpeg
            effect_type = random.choice(['kaleidoscope', 'pulse', 'swirl'])
            processed_path = _apply_effect(video_path, output_path, effect_type)
            
            if processed_path:
                processed_videos.append(processed_path)
                logger.info(f"Applied {effect_type} effect to {video_path}")
            
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
    
    logger.info(f"Processed {len(processed_videos)} videos with hypnotic effects")
    return processed_videos

def _apply_effect(input_path, output_path, effect_type):
    """
    Apply specific hypnotic effect to video using FFmpeg.
    
    Args:
        input_path (str): Input video path
        output_path (str): Output video path
        effect_type (str): Type of effect to apply
    
    Returns:
        str: Path to processed video or None if failed
    """
    ffmpeg_cmd = ['ffmpeg', '-y', '-i', input_path]
    
    if effect_type == 'kaleidoscope':
        # Apply kaleidoscope effect
        filter_complex = "split=2[a][b];[a]kaleidoscope=pattern=4:angle=0[a1];[b]kaleidoscope=pattern=4:angle=0.5[b1];[a1][b1]blend=all_mode=average"
        ffmpeg_cmd.extend(['-filter_complex', filter_complex])
    
    elif effect_type == 'pulse':
        # Apply pulsating effect
        filter_complex = "eq=brightness='0.5+0.2*sin(2*PI*t/3)':saturation='1+0.5*sin(2*PI*t/5)'"
        ffmpeg_cmd.extend(['-vf', filter_complex])
    
    elif effect_type == 'swirl':
        # Apply swirl effect
        filter_complex = "swirl=angle='PI*sin(t)'"
        ffmpeg_cmd.extend(['-vf', filter_complex])
    
    # Add output settings
    ffmpeg_cmd.extend(['-c:v', 'libx264', '-preset', 'medium', output_path])
    
    try:
        # Run FFmpeg process
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error applying effect: {e}")
        return None 