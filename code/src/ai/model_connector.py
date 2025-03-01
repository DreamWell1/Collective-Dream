#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Factory for creating model connectors based on configuration.
"""

import os
import json
import logging
from importlib import import_module
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ModelConnectorFactory:
    """Factory for creating model connectors."""
    
    def __init__(self):
        """Initialize model connector factory."""
        try:
            # Load models config
            config_path = os.path.join('config', 'models.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.models_config = json.load(f)
            else:
                logger.warning("Models config file not found. Using defaults.")
                self.models_config = {
                    "default_model": "doubao",
                    "models": {
                        "doubao": {
                            "provider": "bytedance",
                            "api_endpoint": "https://open.volcengineapi.com"
                        }
                    }
                }
                
            logger.info(f"Loaded model configurations for {len(self.models_config['models'])} models")
            
        except Exception as e:
            logger.error(f"Error loading models config: {e}")
            # Default configuration
            self.models_config = {
                "default_model": "doubao",
                "models": {
                    "doubao": {
                        "provider": "bytedance",
                        "api_endpoint": "https://open.volcengineapi.com"
                    }
                }
            }
    
    def get_connector(self, model_name=None):
        """
        Get model connector instance.
        
        Args:
            model_name (str, optional): Name of the model
        
        Returns:
            object: Model connector instance
        """
        # Use default model if none specified
        if not model_name:
            model_name = self.models_config.get("default_model", "doubao")
        
        # Get model config
        if model_name not in self.models_config["models"]:
            logger.warning(f"Unknown model: {model_name}, using doubao")
            model_name = "doubao"  # Always fall back to doubao, not claude
            
            # If doubao is not in config, raise error
            if model_name not in self.models_config["models"]:
                raise ValueError(f"No configuration found for model: {model_name}")
        
        model_config = self.models_config["models"][model_name]
        
        # Import connector based on provider
        try:
            if model_name == "doubao":
                # Use our local connector for DouBao
                from src.ai.model_connectors.doubao_connector import DouBaoConnector
                return DouBaoConnector(config=model_config)
            else:
                provider = model_config.get("provider", "").lower()
                
                if not provider:
                    logger.error(f"No provider specified for model: {model_name}")
                    raise ValueError(f"No provider specified for model: {model_name}")
                
                # Dynamic import
                try:
                    module_path = f"src.ai.model_connectors.{provider}_connector"
                    module = import_module(module_path)
                    
                    # Get connector class (usually CapitalizedName)
                    class_name = f"{provider.capitalize()}Connector"
                    connector_class = getattr(module, class_name)
                    
                    return connector_class(config=model_config)
                    
                except (ImportError, AttributeError) as e:
                    logger.error(f"Error importing connector for provider {provider}: {e}")
                    # Always fall back to doubao
                    logger.info("Falling back to DouBao")
                    from src.ai.model_connectors.doubao_connector import DouBaoConnector
                    return DouBaoConnector(config=self.models_config["models"]["doubao"])
                
        except Exception as e:
            logger.error(f"Error creating connector for model {model_name}: {e}")
            raise
    
    def get_default_connector(self):
        """
        Get default model connector instance.
        
        Returns:
            object: Model connector instance
        """
        return self.get_connector(self.models_config.get("default_model"))

# Create a global factory instance
_factory = ModelConnectorFactory()

# Add the missing function that main.py is trying to import
def get_ai_model(model_name=None):
    """
    Get an AI model connector.
    
    Args:
        model_name (str, optional): Name of the model to use
        
    Returns:
        object: Model connector instance
    """
    return _factory.get_connector(model_name)

# Available model connectors and their mappings
MODEL_CONNECTORS = {
    "gemini": "gemini_connector",
    "doubao": "doubao_connector",
    "openai": "openai_connector",
    "deepseek": "deepseek_connector",
    "default": "gemini_connector"  # Set Gemini as the default
}

# Model name aliases
MODEL_ALIASES = {
    "gemini": ["gemini", "gemini-pro", "gemini-1.0-pro", "gemini-2.0-flash"],
    "deepseek": ["deepseek", "deepseek-coder", "deepseek-chat"],
    "doubao": ["doubao", "doubao-llama3", "llama3"],
    "openai": ["openai", "gpt", "gpt-3.5", "gpt-4", "chatgpt"]
}

def get_connector_for_model(model_name: str) -> Any:
    """
    Get the appropriate connector for the specified model.
    
    Args:
        model_name: Name of the model to use
        
    Returns:
        Connector module for the requested model
    """
    model_type = model_name.lower().split('-')[0] if '-' in model_name else model_name.lower()
    
    # Check if model_name matches any alias
    connector_name = None
    for connector, aliases in MODEL_ALIASES.items():
        if model_type in aliases or model_name.lower() in aliases:
            connector_name = connector
            break
    
    # If no match found, use default
    if not connector_name:
        logger.warning(f"Unknown model: {model_name}, using {MODEL_CONNECTORS['default']}")
        connector_name = MODEL_CONNECTORS['default']
    
    # Import the appropriate connector module
    module_name = MODEL_CONNECTORS.get(connector_name, MODEL_CONNECTORS['default'])
    try:
        # First try to import from model_connectors package
        return importlib.import_module(f"src.ai.model_connectors.{module_name}")
    except ImportError:
        try:
            # Then try to import directly
            return importlib.import_module(f"src.ai.{module_name}")
        except ImportError:
            logger.error(f"Could not import connector module for {connector_name}")
            # Fall back to the gemini connector that we've created
            from src.ai import text_generator_gemini
            return text_generator_gemini

def generate_text(model_name: str, prompt: str, **kwargs) -> str:
    """
    Generate text using the specified model.
    
    Args:
        model_name: Name of the model to use
        prompt: Text prompt to generate from
        **kwargs: Additional arguments to pass to the model
        
    Returns:
        Generated text
    """
    connector = get_connector_for_model(model_name)
    logger.info(f"Using connector: {connector.__name__} for model: {model_name}")
    
    # Use the connector's generate_text function
    if hasattr(connector, "generate_text"):
        return connector.generate_text(model_name, prompt, **kwargs)
    else:
        logger.error(f"Connector {connector.__name__} does not have generate_text method")
        return f"Error: Model connector {connector.__name__} does not support text generation" 