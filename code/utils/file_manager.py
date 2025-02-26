#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File management utilities for the content generation system.
"""

import os
import shutil
import logging
import json
import tempfile
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class FileManager:
    """Manages file operations for content generation system."""
    
    def __init__(self, base_dir=None):
        """
        Initialize file manager.
        
        Args:
            base_dir (str, optional): Base directory for file operations
        """
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Ensure necessary directories exist
        self.dirs = {
            'data': os.path.join(self.base_dir, 'data'),
            'config': os.path.join(self.base_dir, 'config'),
            'output': os.path.join(self.base_dir, 'data', 'output'),
            'video_library': os.path.join(self.base_dir, 'data', 'video_library'),
            'user_prompts': os.path.join(self.base_dir, 'data', 'user_prompts'),
            'temp': os.path.join(self.base_dir, 'data', 'temp')
        }
        
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def get_unique_filename(self, directory, prefix="file", extension="txt"):
        """
        Generate a unique filename based on timestamp and random hash.
        
        Args:
            directory (str): Directory to save file in
            prefix (str): Filename prefix
            extension (str): File extension without dot
        
        Returns:
            str: Unique file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hash = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        filename = f"{prefix}_{timestamp}_{random_hash}.{extension}"
        return os.path.join(directory, filename)
    
    def save_text_content(self, content, prefix="text", directory=None):
        """
        Save text content to file.
        
        Args:
            content (str): Text content to save
            prefix (str): Filename prefix
            directory (str, optional): Directory to save in, defaults to user_prompts
        
        Returns:
            str: Path to saved file
        """
        directory = directory or self.dirs['user_prompts']
        filepath = self.get_unique_filename(directory, prefix, "txt")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Text content saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving text content: {e}")
            return None
    
    def save_json_data(self, data, prefix="data", directory=None):
        """
        Save JSON data to file.
        
        Args:
            data (dict): Data to save as JSON
            prefix (str): Filename prefix
            directory (str, optional): Directory to save in, defaults to data
        
        Returns:
            str: Path to saved file
        """
        directory = directory or self.dirs['data']
        filepath = self.get_unique_filename(directory, prefix, "json")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logger.info(f"JSON data saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving JSON data: {e}")
            return None
    
    def load_json_file(self, filepath):
        """
        Load JSON data from file.
        
        Args:
            filepath (str): Path to JSON file
        
        Returns:
            dict: Loaded JSON data or None if error
        """
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.error(f"JSON file not found: {filepath}")
                return None
        except Exception as e:
            logger.error(f"Error loading JSON file: {e}")
            return None
    
    def copy_file(self, source_path, dest_directory=None, new_filename=None):
        """
        Copy file to destination directory.
        
        Args:
            source_path (str): Source file path
            dest_directory (str, optional): Destination directory
            new_filename (str, optional): New filename
        
        Returns:
            str: Path to copied file
        """
        if not os.path.exists(source_path):
            logger.error(f"Source file not found: {source_path}")
            return None
        
        dest_directory = dest_directory or self.dirs['output']
        filename = new_filename or os.path.basename(source_path)
        dest_path = os.path.join(dest_directory, filename)
        
        try:
            os.makedirs(dest_directory, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied {source_path} to {dest_path}")
            return dest_path
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            return None
    
    def move_file(self, source_path, dest_directory=None, new_filename=None):
        """
        Move file to destination directory.
        
        Args:
            source_path (str): Source file path
            dest_directory (str, optional): Destination directory
            new_filename (str, optional): New filename
        
        Returns:
            str: Path to moved file
        """
        if not os.path.exists(source_path):
            logger.error(f"Source file not found: {source_path}")
            return None
        
        dest_directory = dest_directory or self.dirs['output']
        filename = new_filename or os.path.basename(source_path)
        dest_path = os.path.join(dest_directory, filename)
        
        try:
            os.makedirs(dest_directory, exist_ok=True)
            shutil.move(source_path, dest_path)
            logger.info(f"Moved {source_path} to {dest_path}")
            return dest_path
        except Exception as e:
            logger.error(f"Error moving file: {e}")
            return None
    
    def create_temp_directory(self):
        """
        Create a temporary directory for processing.
        
        Returns:
            str: Path to temporary directory
        """
        try:
            temp_dir = tempfile.mkdtemp(dir=self.dirs['temp'])
            logger.info(f"Created temporary directory: {temp_dir}")
            return temp_dir
        except Exception as e:
            logger.error(f"Error creating temporary directory: {e}")
            return None
    
    def cleanup_temp_files(self, older_than_days=7):
        """
        Clean up temporary files older than specified days.
        
        Args:
            older_than_days (int): Age threshold in days
        
        Returns:
            int: Number of files deleted
        """
        temp_dir = self.dirs['temp']
        count = 0
        now = datetime.now()
        
        try:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_age = datetime.fromtimestamp(os.path.getmtime(file_path))
                    age_in_days = (now - file_age).days
                    
                    if age_in_days > older_than_days:
                        os.remove(file_path)
                        count += 1
            
            # Also clean empty directories
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
            
            logger.info(f"Cleaned up {count} temporary files older than {older_than_days} days")
            return count
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {e}")
            return 0
    
    def get_file_info(self, filepath):
        """
        Get file information.
        
        Args:
            filepath (str): Path to file
        
        Returns:
            dict: File information
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return None
        
        try:
            stat_info = os.stat(filepath)
            file_info = {
                'path': filepath,
                'filename': os.path.basename(filepath),
                'directory': os.path.dirname(filepath),
                'size': stat_info.st_size,
                'created': datetime.fromtimestamp(stat_info.st_ctime),
                'modified': datetime.fromtimestamp(stat_info.st_mtime),
                'extension': os.path.splitext(filepath)[1].lower(),
                'is_video': os.path.splitext(filepath)[1].lower() in ['.mp4', '.mov', '.avi', '.mkv'],
                'is_audio': os.path.splitext(filepath)[1].lower() in ['.mp3', '.wav', '.ogg', '.flac'],
                'is_image': os.path.splitext(filepath)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif']
            }
            return file_info
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
    
    def scan_video_library(self):
        """
        Scan video library directory and return file information.
        
        Returns:
            dict: Dictionary of category: [files] mappings
        """
        library = {}
        video_dir = self.dirs['video_library']
        
        try:
            for root, dirs, files in os.walk(video_dir):
                # Get category from directory structure
                # The immediate subdirectory under video_library is the category
                rel_path = os.path.relpath(root, video_dir)
                if rel_path == '.':
                    category = 'uncategorized'
                else:
                    category = rel_path.split(os.sep)[0]
                
                if category not in library:
                    library[category] = []
                
                for file in files:
                    if file.endswith(('.mp4', '.mov', '.avi', '.mkv')):
                        file_path = os.path.join(root, file)
                        file_info = self.get_file_info(file_path)
                        if file_info:
                            library[category].append(file_info)
            
            logger.info(f"Scanned video library: {sum(len(files) for files in library.values())} videos in {len(library)} categories")
            return library
        except Exception as e:
            logger.error(f"Error scanning video library: {e}")
            return {} 