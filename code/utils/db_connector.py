#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database connection utilities for the content generation system.
"""

import os
import json
import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseConnector:
    """Manages database connections and operations."""
    
    def __init__(self, db_path=None):
        """
        Initialize database connector.
        
        Args:
            db_path (str, optional): Path to SQLite database file
        """
        if not db_path:
            data_dir = os.path.join('data')
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'content_generation.db')
        
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """
        Establish database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.cursor = None
                logger.info("Disconnected from database")
        except Exception as e:
            logger.error(f"Error disconnecting from database: {e}")
    
    def initialize_database(self):
        """
        Initialize database schema if not exists.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connect():
            return False
        
        try:
            # Create tables if they don't exist
            
            # User inputs table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Generated content table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_id INTEGER NOT NULL,
                text_content TEXT,
                video_path TEXT,
                audio_path TEXT,
                subtitle_path TEXT,
                output_path TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (input_id) REFERENCES user_inputs (id)
            )
            ''')
            
            # Video library table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                title TEXT,
                description TEXT,
                tags TEXT,
                duration REAL,
                width INTEGER,
                height INTEGER,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            self.connection.commit()
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False
        finally:
            self.disconnect()
    
    def save_user_input(self, input_type, content):
        """
        Save user input to database.
        
        Args:
            input_type (str): Type of input ('label' or 'prompt')
            content (str or list): Input content
        
        Returns:
            int: ID of inserted record, or None on error
        """
        if not self.connect():
            return None
        
        try:
            # Convert list to JSON string if necessary
            if isinstance(content, list):
                content = json.dumps(content)
            
            # Insert record
            self.cursor.execute(
                "INSERT INTO user_inputs (input_type, content) VALUES (?, ?)",
                (input_type, content)
            )
            self.connection.commit()
            
            # Get the ID of the inserted record
            input_id = self.cursor.lastrowid
            logger.info(f"Saved user input with ID: {input_id}")
            return input_id
            
        except Exception as e:
            logger.error(f"Error saving user input: {e}")
            return None
        finally:
            self.disconnect()
    
    def save_generated_content(self, input_id, text_content=None, video_path=None, 
                              audio_path=None, subtitle_path=None, output_path=None):
        """
        Save generated content information to database.
        
        Args:
            input_id (int): ID of corresponding user input
            text_content (str, optional): Generated text content
            video_path (str, optional): Path to video file
            audio_path (str, optional): Path to audio file
            subtitle_path (str, optional): Path to subtitle file
            output_path (str, optional): Path to final output file
        
        Returns:
            int: ID of inserted record, or None on error
        """
        if not self.connect():
            return None
        
        try:
            # Insert record
            self.cursor.execute(
                """INSERT INTO generated_content 
                   (input_id, text_content, video_path, audio_path, subtitle_path, output_path) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (input_id, text_content, video_path, audio_path, subtitle_path, output_path)
            )
            self.connection.commit()
            
            # Get the ID of the inserted record
            content_id = self.cursor.lastrowid
            logger.info(f"Saved generated content with ID: {content_id}")
            return content_id
            
        except Exception as e:
            logger.error(f"Error saving generated content: {e}")
            return None
        finally:
            self.disconnect()
    
    def register_video(self, path, category, title=None, description=None, 
                       tags=None, duration=None, width=None, height=None):
        """
        Register a video in the library.
        
        Args:
            path (str): Path to video file
            category (str): Video category
            title (str, optional): Video title
            description (str, optional): Video description
            tags (list, optional): Video tags
            duration (float, optional): Video duration in seconds
            width (int, optional): Video width in pixels
            height (int, optional): Video height in pixels
        
        Returns:
            int: ID of inserted record, or None on error
        """
        if not self.connect():
            return None
        
        try:
            # Convert tags list to JSON string if necessary
            if isinstance(tags, list):
                tags = json.dumps(tags)
            
            # Check if video already exists
            self.cursor.execute(
                "SELECT id FROM video_library WHERE path = ?",
                (path,)
            )
            existing = self.cursor.fetchone()
            
            if existing:
                # Update existing record
                self.cursor.execute(
                    """UPDATE video_library 
                       SET category = ?, title = ?, description = ?, 
                           tags = ?, duration = ?, width = ?, height = ? 
                       WHERE path = ?""",
                    (category, title, description, tags, duration, width, height, path)
                )
                video_id = existing[0]
                logger.info(f"Updated video record with ID: {video_id}")
            else:
                # Insert new record
                self.cursor.execute(
                    """INSERT INTO video_library 
                       (path, category, title, description, tags, duration, width, height) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (path, category, title, description, tags, duration, width, height)
                )
                video_id = self.cursor.lastrowid
                logger.info(f"Registered new video with ID: {video_id}")
            
            self.connection.commit()
            return video_id
            
        except Exception as e:
            logger.error(f"Error registering video: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_videos_by_category(self, category):
        """
        Get videos by category.
        
        Args:
            category (str): Video category
        
        Returns:
            list: List of video records
        """
        if not self.connect():
            return []
        
        try:
            self.cursor.execute(
                "SELECT * FROM video_library WHERE category = ?",
                (category,)
            )
            videos = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = [col[0] for col in self.cursor.description]
            result = []
            for video in videos:
                video_dict = dict(zip(columns, video))
                
                # Parse JSON strings
                if video_dict.get('tags') and isinstance(video_dict['tags'], str):
                    try:
                        video_dict['tags'] = json.loads(video_dict['tags'])
                    except:
                        video_dict['tags'] = []
                
                result.append(video_dict)
            
            logger.info(f"Retrieved {len(result)} videos for category: {category}")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving videos: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_recent_generations(self, limit=10):
        """
        Get recent content generations.
        
        Args:
            limit (int): Maximum number of records to retrieve
        
        Returns:
            list: List of generation records with user input
        """
        if not self.connect():
            return []
        
        try:
            self.cursor.execute(
                """SELECT g.*, u.input_type, u.content 
                   FROM generated_content g
                   JOIN user_inputs u ON g.input_id = u.id
                   ORDER BY g.timestamp DESC
                   LIMIT ?""",
                (limit,)
            )
            generations = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = [col[0] for col in self.cursor.description]
            result = []
            for gen in generations:
                gen_dict = dict(zip(columns, gen))
                result.append(gen_dict)
            
            logger.info(f"Retrieved {len(result)} recent generations")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving recent generations: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_generation_by_id(self, generation_id):
        """
        Get a specific content generation by ID.
        
        Args:
            generation_id (int): ID of generation record
        
        Returns:
            dict: Generation record with user input, or None if not found
        """
        if not self.connect():
            return None
        
        try:
            self.cursor.execute(
                """SELECT g.*, u.input_type, u.content 
                   FROM generated_content g
                   JOIN user_inputs u ON g.input_id = u.id
                   WHERE g.id = ?""",
                (generation_id,)
            )
            gen = self.cursor.fetchone()
            
            if not gen:
                logger.warning(f"Generation with ID {generation_id} not found")
                return None
            
            # Convert to dictionary
            columns = [col[0] for col in self.cursor.description]
            gen_dict = dict(zip(columns, gen))
            
            logger.info(f"Retrieved generation with ID: {generation_id}")
            return gen_dict
            
        except Exception as e:
            logger.error(f"Error retrieving generation: {e}")
            return None
        finally:
            self.disconnect()
    
    def delete_generation(self, generation_id):
        """
        Delete a generation record.
        
        Args:
            generation_id (int): ID of generation to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connect():
            return False
        
        try:
            # Get input_id first
            self.cursor.execute(
                "SELECT input_id FROM generated_content WHERE id = ?",
                (generation_id,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                logger.warning(f"Generation with ID {generation_id} not found")
                return False
            
            input_id = result[0]
            
            # Delete generation record
            self.cursor.execute(
                "DELETE FROM generated_content WHERE id = ?",
                (generation_id,)
            )
            
            # Delete corresponding input record
            self.cursor.execute(
                "DELETE FROM user_inputs WHERE id = ?",
                (input_id,)
            )
            
            self.connection.commit()
            logger.info(f"Deleted generation with ID: {generation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting generation: {e}")
            return False
        finally:
            self.disconnect()
    
    def search_videos(self, query):
        """
        Search videos by title, description, or tags.
        
        Args:
            query (str): Search query
        
        Returns:
            list: List of matching video records
        """
        if not self.connect():
            return []
        
        try:
            # Use LIKE for basic text search
            search_term = f"%{query}%"
            self.cursor.execute(
                """SELECT * FROM video_library 
                   WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
                   ORDER BY id DESC""",
                (search_term, search_term, search_term)
            )
            videos = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = [col[0] for col in self.cursor.description]
            result = []
            for video in videos:
                video_dict = dict(zip(columns, video))
                
                # Parse JSON strings
                if video_dict.get('tags') and isinstance(video_dict['tags'], str):
                    try:
                        video_dict['tags'] = json.loads(video_dict['tags'])
                    except:
                        video_dict['tags'] = []
                
                result.append(video_dict)
            
            logger.info(f"Found {len(result)} videos matching query: {query}")
            return result
            
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            return []
        finally:
            self.disconnect() 