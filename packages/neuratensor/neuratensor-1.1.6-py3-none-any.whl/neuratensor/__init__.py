"""
NeuraTensor SDK - Public API
=============================

Production-ready neuromorphic inference SDK with universal hardware support.

Public API for NeuraTensor models. The core CUDA kernels are proprietary
and distributed as compiled binaries.

Neuramorphic, Inc. - San Francisco, CA
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Neuramorphic, Inc."
__license__ = "Apache 2.0"

from .model_loader import ModelLoader
from .config import SDKConfig, NeuraTensorConfig, ModelSize


class NeuraTensor:
    """
    NeuraTensor neuromorphic model (Public API).
    
    Example:
        >>> config = NeuraTensorConfig.preset("64m")
        >>> model = NeuraTensor(config).cuda()
    """
    def __init__(self, config: NeuraTensorConfig):
        import sys
        import os
        from pathlib import Path
        
        # Enable internal imports (SDK is authorized)
        os.environ["NEURATENSOR_INTERNAL"] = "1"
        
        # Add parent directories to path
        sdk_dir = Path(__file__).parent
        neuratensor_root = sdk_dir.parent
        sys.path.insert(0, str(neuratensor_root))
        
        # Import from internal implementation
        try:
            from core.model import NeuraTensorModel
            from config.presets import create_64m_config, create_256m_config, create_1b_config
        except ImportError as e:
            raise RuntimeError(
                f"Internal modules not found. This SDK requires the full NeuraTensor distribution.\n"
                f"Error: {e}\n"
                f"If you installed from PyPI, please contact support@neuramorphic.ai"
            )
        
        # Map SDK config to internal config
        preset_map = {
            "64m": create_64m_config,
            "256m": create_256m_config,
            "1b": create_1b_config,
        }
        
        model_size = config.model_size.value if hasattr(config.model_size, 'value') else config.model_size
        
        if model_size not in preset_map:
            raise ValueError(f"Unknown model size: {model_size}. Available: {list(preset_map.keys())}")
        
        # Create internal config and model
        internal_config = preset_map[model_size]()
        self._model = NeuraTensorModel(internal_config)
        self.config = config
        
        # Update SDK config with internal values
        self.config.vocab_size = internal_config.vocab_size
        self.config.hidden_size = internal_config.hidden_size
    
    def cuda(self):
        """Move model to CUDA"""
        self._model = self._model.cuda()
        return self
    
    def half(self):
        """Convert model to FP16"""
        self._model = self._model.half()
        return self
    
    def __call__(self, input_ids):
        """Forward pass"""
        result = self._model(input_ids)
        # Return logits if dict, otherwise return as-is
        if isinstance(result, dict):
            return result.get('logits', result)
        return result
    
    def count_parameters(self):
        """Count model parameters"""
        return self._model.count_parameters()
    
    def parameters(self):
        """Return iterator over parameters"""
        return self._model.parameters()

__all__ = [
    'NeuraTensor',
    'NeuraTensorConfig',
    'ModelLoader',
    'SDKConfig',
    'ModelSize',
]


# Quick start example
def quick_start():
    """
    Quick start example for NeuraTensor SDK.
    
    Usage:
        >>> from neuratensor.sdk import quick_start
        >>> quick_start()
    """
    print("=" * 70)
    print("NeuraTensor SDK - Quick Start")
    print("=" * 70)
    print()
    print("from neuratensor.sdk import NeuraTensor")
    print()
    print("# Load model")
    print('model = NeuraTensor.from_pretrained("64m")')
    print()
    print("# Run inference")
    print("output = model(input_ids)")
    print()
    print("# Available models: 64m, 256m, 1b")
    print("=" * 70)
