#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Logging utilities for the content generation system.
"""

import os
import logging
import logging.handlers
import sys
from datetime import datetime

def setup_logger(logger_name=None, log_level=logging.INFO, log_file=None, console_output=True):
    """
    Set up a logger with file and console handlers.
    
    Args:
        logger_name (str, optional): Name of the logger
        log_level (int): Logging level
        log_file (str, optional): Path to log file
        console_output (bool): Whether to output to console
    
    Returns:
        logging.Logger: Configured logger
    """
    # Get or create logger
    logger = logging.getLogger(logger_name or __name__)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Set level
    logger.setLevel(log_level)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '[%(levelname)s] - %(message)s'
    )
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if log file provided
    if log_file:
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Create rotating file handler (10 MB max, 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def get_logger(name, log_dir=None):
    """
    Get a configured logger for a specific module.
    
    Args:
        name (str): Name for the logger (usually __name__)
        log_dir (str, optional): Custom log directory
    
    Returns:
        logging.Logger: Configured logger
    """
    if log_dir is None:
        # Default log directory is 'logs' under the project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(base_dir, 'logs')
    
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log filename based on the module name
    module_name = name.split('.')[-1]
    log_file = os.path.join(log_dir, f"{module_name}.log")
    
    # Set up and return logger
    return setup_logger(name, log_file=log_file)

class LoggerManager:
    """Manages loggers for the application."""
    
    def __init__(self, log_dir=None, log_level=logging.INFO):
        """
        Initialize logger manager.
        
        Args:
            log_dir (str, optional): Directory for log files
            log_level (int): Logging level
        """
        # Determine log directory
        if log_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.log_dir = os.path.join(base_dir, 'logs')
        else:
            self.log_dir = log_dir
        
        # Create log directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Store log level
        self.log_level = log_level
        
        # Set up main application logger
        self._setup_app_logger()
    
    def _setup_app_logger(self):
        """Set up the main application logger."""
        # Main log file
        timestamp = datetime.now().strftime("%Y%m%d")
        app_log_file = os.path.join(self.log_dir, f"app_{timestamp}.log")
        
        # Set up main logger
        self.app_logger = setup_logger(
            logger_name="content_generation",
            log_level=self.log_level,
            log_file=app_log_file
        )
        
        # Error log file
        error_log_file = os.path.join(self.log_dir, f"error_{timestamp}.log")
        
        # Add error handler for ERROR and CRITICAL
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=10*1024*1024, backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.app_logger.addHandler(error_handler)
    
    def get_logger(self, name):
        """
        Get a logger for a specific module.
        
        Args:
            name (str): Module name
        
        Returns:
            logging.Logger: Configured logger
        """
        # Create module-specific log file
        module_name = name.split('.')[-1]
        log_file = os.path.join(self.log_dir, f"{module_name}.log")
        
        # Set up and return logger
        return setup_logger(
            logger_name=name,
            log_level=self.log_level,
            log_file=log_file
        )

# Initialize a default logger
default_logger = setup_logger(
    logger_name="content_generation", 
    log_level=logging.INFO
)

def log_function_call(func):
    """
    Decorator to log function calls, arguments, and return values.
    
    Args:
        func: Function to decorate
    
    Returns:
        callable: Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # Log function call with arguments
        args_str = ', '.join([repr(arg) for arg in args])
        kwargs_str = ', '.join([f"{key}={repr(value)}" for key, value in kwargs.items()])
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))
        
        logger.debug(f"Calling {func.__name__}({all_args})")
        
        try:
            # Call the function
            result = func(*args, **kwargs)
            
            # Log success
            logger.debug(f"{func.__name__} returned: {repr(result)}")
            
            return result
        
        except Exception as e:
            # Log exception
            logger.exception(f"Exception in {func.__name__}: {str(e)}")
            raise
    
    return wrapper 