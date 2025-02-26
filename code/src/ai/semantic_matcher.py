#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Calculates semantic similarity between user prompts and video content.
"""

import logging
import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class SemanticMatcher:
    """Matches user prompts with video content based on semantic similarity."""
    
    def __init__(self):
        """Initialize the semantic matcher."""
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.video_metadata = self._load_video_metadata()
    
    def _load_video_metadata(self):
        """
        Load metadata for all videos in the library.
        
        Returns:
            list: List of video metadata dictionaries
        """
        metadata = []
        video_dir = os.path.join('data', 'video_library')
        
        try:
            # Look for metadata files in video directory
            for root, _, files in os.walk(video_dir):
                for file in files:
                    if file.endswith('.json'):
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            video_data = json.load(f)
                            # Add the corresponding video file
                            video_file = file.replace('.json', '.mp4')
                            if os.path.exists(os.path.join(root, video_file)):
                                video_data['video_path'] = os.path.join(root, video_file)
                                metadata.append(video_data)
        except Exception as e:
            logger.error(f"Error loading video metadata: {e}")
        
        logger.info(f"Loaded metadata for {len(metadata)} videos")
        return metadata
    
    def calculate_similarity(self, prompt, video_metadata):
        """
        Calculate similarity between prompt and video metadata.
        
        Args:
            prompt (str): User prompt
            video_metadata (dict): Video metadata
        
        Returns:
            float: Similarity score (0-1)
        """
        # Combine relevant metadata fields
        video_text = " ".join([
            video_metadata.get('title', ''),
            video_metadata.get('description', ''),
            " ".join(video_metadata.get('tags', [])),
            " ".join(video_metadata.get('keywords', []))
        ])
        
        # If there's not enough text to compare, return low similarity
        if len(video_text.strip()) < 10:
            return 0.1
        
        # Calculate TF-IDF vectors and cosine similarity
        try:
            tfidf_matrix = self.vectorizer.fit_transform([prompt, video_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

def match_videos(prompt, video_files=None, top_n=5):
    """
    Match user prompt with videos based on semantic similarity.
    
    Args:
        prompt (str): User prompt or concatenated labels
        video_files (list, optional): List of video file paths to consider
        top_n (int): Number of top matches to return
    
    Returns:
        list: List of (video_path, similarity_score) tuples, sorted by similarity
    """
    matcher = SemanticMatcher()
    results = []
    
    # Filter video metadata based on provided files if any
    videos_to_check = matcher.video_metadata
    if video_files:
        videos_to_check = [v for v in videos_to_check if v.get('video_path') in video_files]
    
    # Calculate similarity for each video
    for video in videos_to_check:
        if 'video_path' in video:
            similarity = matcher.calculate_similarity(prompt, video)
            results.append((video['video_path'], similarity))
    
    # Sort by similarity (descending) and return top N
    results.sort(key=lambda x: x[1], reverse=True)
    top_results = results[:top_n]
    
    logger.info(f"Top {len(top_results)} video matches found with scores: {[score for _, score in top_results]}")
    return top_results 