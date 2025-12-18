"""
Model Loader
============

Utilities for loading and managing NeuraTensor models.
"""

import os
import torch
from pathlib import Path
from typing import Optional, Dict, Any
import json


class ModelLoader:
    """
    Model loading and management utilities.
    
    Handles model caching, downloading, and version management.
    """
    
    DEFAULT_CACHE_DIR = Path.home() / ".cache" / "neuratensor"
    
    @staticmethod
    def get_cache_dir() -> Path:
        """Get or create cache directory"""
        cache_dir = os.environ.get("NEURATENSOR_CACHE", ModelLoader.DEFAULT_CACHE_DIR)
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    
    @staticmethod
    def list_cached_models() -> list:
        """
        List all cached models.
        
        Returns:
            List of cached model names
        """
        cache_dir = ModelLoader.get_cache_dir()
        
        if not cache_dir.exists():
            return []
        
        models = []
        for model_dir in cache_dir.iterdir():
            if model_dir.is_dir():
                config_file = model_dir / "config.json"
                if config_file.exists():
                    models.append(model_dir.name)
        
        return models
    
    @staticmethod
    def get_model_path(model_name: str) -> Optional[Path]:
        """
        Get path to cached model.
        
        Args:
            model_name: Model identifier
        
        Returns:
            Path to model or None if not cached
        """
        cache_dir = ModelLoader.get_cache_dir()
        model_path = cache_dir / model_name
        
        if model_path.exists():
            return model_path
        
        return None
    
    @staticmethod
    def save_model(model, model_name: str, config: Dict[str, Any]):
        """
        Save model to cache.
        
        Args:
            model: Model instance
            model_name: Model identifier
            config: Model configuration
        """
        cache_dir = ModelLoader.get_cache_dir()
        model_path = cache_dir / model_name
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Save config
        config_file = model_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Save weights (if model has state_dict)
        if hasattr(model, 'state_dict'):
            weights_file = model_path / "model.pt"
            torch.save(model.state_dict(), weights_file)
    
    @staticmethod
    def load_model(model_name: str):
        """
        Load model from cache.
        
        Args:
            model_name: Model identifier
        
        Returns:
            Loaded model instance
        """
        model_path = ModelLoader.get_model_path(model_name)
        
        if model_path is None:
            raise FileNotFoundError(f"Model '{model_name}' not found in cache")
        
        # Load config
        config_file = model_path / "config.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Load weights
        weights_file = model_path / "model.pt"
        if weights_file.exists():
            state_dict = torch.load(weights_file, map_location='cpu')
            return state_dict, config
        
        return None, config
    
    @staticmethod
    def clear_cache(model_name: Optional[str] = None):
        """
        Clear model cache.
        
        Args:
            model_name: Specific model to remove, or None to clear all
        """
        cache_dir = ModelLoader.get_cache_dir()
        
        if model_name:
            model_path = cache_dir / model_name
            if model_path.exists():
                import shutil
                shutil.rmtree(model_path)
        else:
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
    
    @staticmethod
    def get_model_info(model_name: str) -> Dict[str, Any]:
        """
        Get information about cached model.
        
        Args:
            model_name: Model identifier
        
        Returns:
            Model metadata
        """
        model_path = ModelLoader.get_model_path(model_name)
        
        if model_path is None:
            return {'cached': False}
        
        config_file = model_path / "config.json"
        weights_file = model_path / "model.pt"
        
        info = {
            'cached': True,
            'path': str(model_path),
            'has_config': config_file.exists(),
            'has_weights': weights_file.exists(),
        }
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                info['config'] = json.load(f)
        
        if weights_file.exists():
            info['weights_size_mb'] = weights_file.stat().st_size / 1024 / 1024
        
        return info
