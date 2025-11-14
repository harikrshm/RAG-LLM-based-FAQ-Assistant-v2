"""
Configuration Loader Utility

Loads Groww page mapping configuration from JSON or YAML files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Utility class for loading configuration files."""
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is invalid JSON
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        logger.info(f"Loaded configuration from {file_path}")
        return config
    
    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ImportError: If PyYAML is not installed
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required to load YAML files. Install with: pip install pyyaml")
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from {file_path}")
        return config
    
    @staticmethod
    def load_groww_mappings(config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load Groww page mapping configuration.
        
        Tries JSON first, then YAML if JSON doesn't exist.
        
        Args:
            config_path: Optional path to config file. If None, uses settings.GROWW_MAPPINGS_PATH
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If neither JSON nor YAML file exists
        """
        if config_path is None:
            config_path = settings.GROWW_MAPPINGS_PATH
        
        path = Path(config_path)
        
        # Try JSON first
        json_path = path.with_suffix(".json")
        if json_path.exists():
            return ConfigLoader.load_json(str(json_path))
        
        # Try YAML
        yaml_path = path.with_suffix(".yaml")
        if yaml_path.exists():
            return ConfigLoader.load_yaml(str(yaml_path))
        
        # Try exact path
        if path.exists():
            if path.suffix.lower() == ".json":
                return ConfigLoader.load_json(str(path))
            elif path.suffix.lower() in [".yaml", ".yml"]:
                return ConfigLoader.load_yaml(str(path))
        
        raise FileNotFoundError(
            f"Groww mappings configuration not found. "
            f"Tried: {json_path}, {yaml_path}, {path}"
        )


# Singleton cache for configuration
_config_cache: Optional[Dict[str, Any]] = None


def get_groww_mappings() -> Dict[str, Any]:
    """
    Get Groww page mapping configuration (cached).
    
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
    """
    global _config_cache
    
    if _config_cache is None:
        try:
            _config_cache = ConfigLoader.load_groww_mappings()
        except FileNotFoundError as e:
            logger.warning(f"Could not load Groww mappings config: {e}")
            logger.warning("Using default empty configuration")
            _config_cache = {
                "amc_mappings": {},
                "url_patterns": {},
                "query_patterns": {},
                "information_categories": {},
                "page_sections": {},
                "base_url": "https://groww.in",
            }
    
    return _config_cache


def reload_groww_mappings() -> Dict[str, Any]:
    """
    Reload Groww page mapping configuration (clears cache).
    
    Returns:
        Configuration dictionary
    """
    global _config_cache
    _config_cache = None
    return get_groww_mappings()

