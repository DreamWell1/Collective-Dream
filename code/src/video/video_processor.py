#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Processes video content based on user selection.
"""

import os
import logging
from src.video.video_library import get_videos_by_label, get_video_metadata

logger = logging.getLogger(__name__)

def process_videos(selected_labels=None):
    """
    Process videos based on selected labels.
    If no labels provided, return all available videos.
    
    Args:
        selected_labels (list, optional): List of selected label dictionaries
    
    Returns:
        list: List of processed video file paths
    """
    video_files = []
    
    if selected_labels:
        for label_data in selected_labels:
            label_name = label_data['name']
            label_videos = get_videos_by_label(label_name)
            video_files.extend(label_videos)
    else:
        # Get all videos if no labels specified
        video_dir = os.path.join('data', 'video_library')
        for root, _, files in os.walk(video_dir):
            for file in files:
                if file.endswith('.mp4'):
                    video_files.append(os.path.join(root, file))
    
    logger.info(f"Processed {len(video_files)} video files")
    return video_files

def filter_videos_by_duration(video_files, min_duration=5, max_duration=60):
    """
    Filter videos by duration.
    
    Args:
        video_files (list): List of video file paths
        min_duration (int): Minimum duration in seconds
        max_duration (int): Maximum duration in seconds
    
    Returns:
        list: Filtered video file paths
    """
    filtered_videos = []
    
    for video_path in video_files:
        metadata = get_video_metadata(video_path)
        duration = metadata.get('duration', 0)
        
        if min_duration <= duration <= max_duration:
            filtered_videos.append(video_path)
    
    logger.info(f"Filtered {len(video_files)} videos to {len(filtered_videos)} " +
                f"based on duration ({min_duration}-{max_duration}s)")
    return filtered_videos

def sort_videos_by_quality(video_files, min_resolution=(720, 480)):
    """
    Sort videos by quality (resolution).
    
    Args:
        video_files (list): List of video file paths
        min_resolution (tuple): Minimum acceptable resolution (width, height)
    
    Returns:
        list: Sorted video file paths (higher quality first)
    """
    video_quality = []
    
    for video_path in video_files:
        metadata = get_video_metadata(video_path)
        width = metadata.get('width', 0)
        height = metadata.get('height', 0)
        
        # Skip videos below minimum resolution
        if width < min_resolution[0] or height < min_resolution[1]:
            continue
        
        # Calculate quality score (simple product of dimensions)
        quality_score = width * height
        video_quality.append((video_path, quality_score))
    
    # Sort by quality score (descending)
    video_quality.sort(key=lambda x: x[1], reverse=True)
    sorted_videos = [v for v, _ in video_quality]
    
    logger.info(f"Sorted {len(sorted_videos)} videos by quality")
    return sorted_videos 