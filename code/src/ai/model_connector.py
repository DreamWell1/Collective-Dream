#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Factory for creating model connectors based on configuration.
"""

import os
import json
import logging
from importlib import import_module

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