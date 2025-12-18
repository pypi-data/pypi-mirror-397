"""
SDK Configuration
=================

Public configuration interface for NeuraTensor SDK.

IMPORTANT: This is the ONLY configuration interface for SDK users.
Never import from core.config or config.presets directly.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Union, List

# Alias for backward compatibility
NeuraTensorConfig = None  # Will be defined below


class ModelSize(Enum):
    """Predefined model sizes"""
    M64 = "64m"
    M256 = "256m"
    B1 = "1b"
    
    @classmethod
    def from_string(cls, size: str) -> 'ModelSize':
        """Convert string to ModelSize"""
        size_map = {
            "64m": cls.M64,
            "256m": cls.M256,
            "1b": cls.B1,
        }
        if size not in size_map:
            raise ValueError(f"Unknown model size: {size}. Available: {list(size_map.keys())}")
        return size_map[size]


class Backend(Enum):
    """Hardware backends"""
    AUTO = "auto"
    JETSON_ORIN = "jetson_orin"
    JETSON_AGX = "jetson_agx"
    NVIDIA_DESKTOP = "nvidia_desktop"
    CUDA_GENERIC = "cuda_generic"


class Precision(Enum):
    """Model precision"""
    FP32 = "float32"
    FP16 = "float16"
    INT8 = "int8"


@dataclass
class SDKConfig:
    """
    SDK Configuration for NeuraTensor models.
    
    This is the public configuration interface. Internal model parameters
    are managed by the proprietary core.
    
    Args:
        model_size: Model size ('64m', '256m', '1b')
        backend: Hardware backend (auto-detected by default)
        precision: Model precision (fp32, fp16, int8)
        batch_size: Maximum batch size
        max_sequence_length: Maximum input sequence length
        device: Device ID or 'cuda'/'cpu'
        cache_dir: Directory for model cache
        use_flash_attention: Enable flash attention optimization
        compile_mode: JIT compilation mode ('none', 'default', 'max-autotune')
    """
    
    model_size: Union[str, ModelSize] = "64m"
    backend: Union[str, Backend] = "auto"
    precision: Union[str, Precision] = "float16"
    batch_size: int = 1
    max_sequence_length: int = 64
    device: str = "cuda"
    cache_dir: Optional[str] = None
    use_flash_attention: bool = True
    compile_mode: str = "default"
    
    # Internal attributes (populated from core)
    vocab_size: Optional[int] = None
    hidden_size: Optional[int] = None
    
    def __post_init__(self):
        """Validate configuration"""
        # Convert strings to enums
        if isinstance(self.model_size, str):
            self.model_size = ModelSize.from_string(self.model_size)
        if isinstance(self.backend, str):
            self.backend = Backend[self.backend.upper()]
        if isinstance(self.precision, str):
            precision_map = {
                "float32": Precision.FP32,
                "fp32": Precision.FP32,
                "float16": Precision.FP16,
                "fp16": Precision.FP16,
                "int8": Precision.INT8,
            }
            self.precision = precision_map.get(self.precision.lower(), Precision.FP16)
        
        # Validate ranges
        if self.batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {self.batch_size}")
        if self.max_sequence_length < 1:
            raise ValueError(f"max_sequence_length must be >= 1, got {self.max_sequence_length}")
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'model_size': self.model_size.value,
            'backend': self.backend.value,
            'precision': self.precision.value,
            'batch_size': self.batch_size,
            'max_sequence_length': self.max_sequence_length,
            'device': self.device,
            'cache_dir': self.cache_dir,
            'use_flash_attention': self.use_flash_attention,
            'compile_mode': self.compile_mode,
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'SDKConfig':
        """Create from dictionary"""
        return cls(**config_dict)
    
    @classmethod
    def preset(cls, model_name: str) -> 'SDKConfig':
        """
        Create configuration from preset.
        
        Args:
            model_name: Model preset ('64m', '256m', '1b')
        
        Returns:
            SDKConfig instance with preset parameters
        
        Example:
            >>> config = SDKConfig.preset("64m")
            >>> model = NeuraTensor(config)
        """
        # Map preset names to configurations
        presets = {
            "64m": {
                "model_size": "64m",
                "max_sequence_length": 64,
                "batch_size": 1,
                "precision": "float16",
                "vocab_size": 50000,
                "hidden_size": 1280,
            },
            "256m": {
                "model_size": "256m",
                "max_sequence_length": 128,
                "batch_size": 4,
                "precision": "float16",
                "vocab_size": 50000,
                "hidden_size": 2048,
            },
            "1b": {
                "model_size": "1b",
                "max_sequence_length": 256,
                "batch_size": 8,
                "precision": "float16",
                "vocab_size": 50000,
                "hidden_size": 3072,
            },
        }
        
        if model_name not in presets:
            raise ValueError(
                f"Unknown preset: {model_name}. "
                f"Available: {list(presets.keys())}"
            )
        
        return cls(**presets[model_name])
    
    def __repr__(self) -> str:
        return (
            f"SDKConfig(\n"
            f"  model_size={self.model_size.value},\n"
            f"  backend={self.backend.value},\n"
            f"  precision={self.precision.value},\n"
            f"  batch_size={self.batch_size},\n"
            f"  max_sequence_length={self.max_sequence_length},\n"
            f"  device={self.device}\n"
            f")"
        )


@dataclass
class InferenceConfig:
    """
    Runtime inference configuration.
    
    Args:
        temperature: Sampling temperature (0.0 = greedy)
        top_k: Top-k sampling
        top_p: Nucleus sampling
        max_new_tokens: Maximum tokens to generate
        do_sample: Enable sampling (vs greedy)
    """
    
    temperature: float = 1.0
    top_k: int = 50
    top_p: float = 0.95
    max_new_tokens: int = 100
    do_sample: bool = True
    
    def __post_init__(self):
        """Validate inference config"""
        if self.temperature < 0:
            raise ValueError(f"temperature must be >= 0, got {self.temperature}")
        if self.top_k < 1:
            raise ValueError(f"top_k must be >= 1, got {self.top_k}")
        if not 0 <= self.top_p <= 1:
            raise ValueError(f"top_p must be in [0, 1], got {self.top_p}")


# Main config alias for public API
NeuraTensorConfig = SDKConfig
