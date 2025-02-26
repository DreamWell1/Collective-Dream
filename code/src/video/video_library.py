#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functions for accessing and managing the video library.
"""

import os
import random
import logging
from utils.db_connector import DatabaseConnector

logger = logging.getLogger(__name__)

def get_videos_by_label(label, limit=5):
    """
    Get videos by label/category.
    
    Args:
        label (str): Video category label
        limit (int, optional): Maximum number of videos to return
    
    Returns:
        list: List of video file paths
    """
    try:
        db = DatabaseConnector()
        videos = db.get_videos_by_category(label)
        
        # If no videos in DB, try to find them in the directory
        if not videos:
            video_dir = os.path.join('data', 'video_library', label.lower())
            
            if os.path.exists(video_dir):
                video_files = []
                for file in os.listdir(video_dir):
                    if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                        video_files.append(os.path.join(video_dir, file))
                
                logger.info(f"Found {len(video_files)} videos in directory for label: {label}")
                
                # Randomly select videos up to the limit
                if len(video_files) > limit:
                    return random.sample(video_files, limit)
                return video_files
            
            logger.warning(f"No videos found for label: {label}")
            return []
        
        # Extract paths from database results
        paths = [video['path'] for video in videos]
        
        # Randomly select videos up to the limit
        if len(paths) > limit:
            return random.sample(paths, limit)
        return paths
        
    except Exception as e:
        logger.error(f"Error getting videos by label: {e}")
        return []

def get_video_metadata(video_path):
    """
    Get metadata for a video file.
    
    Args:
        video_path (str): Path to video file
    
    Returns:
        dict: Video metadata
    """
    try:
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None
        
        # Get basic file info
        filename = os.path.basename(video_path)
        size = os.path.getsize(video_path)
        
        # For more detailed metadata, we would normally use moviepy or opencv
        # This is a simplified version
        metadata = {
            'path': video_path,
            'filename': filename,
            'size': size,
            'category': os.path.basename(os.path.dirname(video_path)),
            'duration': 10.0,  # Placeholder
            'width': 1920,     # Placeholder
            'height': 1080     # Placeholder
        }
        
        logger.info(f"Retrieved metadata for video: {filename}")
        return metadata
        
    except Exception as e:
        logger.error(f"Error getting video metadata: {e}")
        return None 