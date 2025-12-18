"""
NeuraTensor Core Module - Proprietary
=====================================
This code is obfuscated and proprietary.
Reverse engineering is prohibited.
© 2024-2025 Neuramorphic, Inc.
"""
""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ModelConfig:
    ""

    vocab_size: int
    hidden_size: int
    max_sequence_length: int

    snn_layers: int
    snn_hidden_size: int
    snn_neurons_per_layer: int

    neurossm_layers: int
    neurossm_hidden_size: int
    neurossm_state_size: int

    dtype: str = "float32"
    mixed_precision: bool = False
    gradient_checkpointing: bool = False
    memory_efficient_attention: bool = False

    device: str = "cuda"
    use_cuda: bool = True

    fast_mode: bool = False
    
    def __post_init__(self):
        ""
        self._validate()
    
    def _validate(self):
        ""

        if self.vocab_size <= 0:
            raise ValueError(f"vocab_size must be positive, got {self.vocab_size}")

        if self.hidden_size <= 0:
            raise ValueError(f"hidden_size must be positive, got {self.hidden_size}")
        
        if self.max_sequence_length <= 0:
            raise ValueError(f"max_sequence_length must be positive, got {self.max_sequence_length}")

        if self.snn_layers <= 0:
            raise ValueError(f"snn_layers must be positive, got {self.snn_layers}")
        
        if self.snn_hidden_size <= 0:
            raise ValueError(f"snn_hidden_size must be positive, got {self.snn_hidden_size}")
        
        if self.snn_neurons_per_layer <= 0:
            raise ValueError(f"snn_neurons_per_layer must be positive, got {self.snn_neurons_per_layer}")

        if self.neurossm_layers <= 0:
            raise ValueError(f"neurossm_layers must be positive, got {self.neurossm_layers}")
        
        if self.neurossm_hidden_size <= 0:
            raise ValueError(f"neurossm_hidden_size must be positive, got {self.neurossm_hidden_size}")
        
        if self.neurossm_state_size <= 0:
            raise ValueError(f"neurossm_state_size must be positive, got {self.neurossm_state_size}")

        valid_dtypes = ["float16", "float32", "bfloat16"]
        if self.dtype not in valid_dtypes:
            raise ValueError(f"dtype must be one of {valid_dtypes}, got {self.dtype}")

        valid_devices = ["cuda", "cpu"]
        if self.device not in valid_devices:
            raise ValueError(f"device must be one of {valid_devices}, got {self.device}")
    
    def get_total_snn_neurons(self) -> int:
        ""
        return self.snn_layers * self.snn_neurons_per_layer
    
    def get_state_size(self) -> int:
        ""
        return self.neurossm_state_size
    
    def summary(self) -> dict:
        ""
        return {
            "architecture": {
                "vocab_size": self.vocab_size,
                "hidden_size": self.hidden_size,
                "max_sequence_length": self.max_sequence_length,
            },
            "snn": {
                "layers": self.snn_layers,
                "hidden_size": self.snn_hidden_size,
                "neurons_per_layer": self.snn_neurons_per_layer,
                "total_neurons": self.get_total_snn_neurons(),
            },
            "ssm": {
                "layers": self.neurossm_layers,
                "hidden_size": self.neurossm_hidden_size,
                "state_size": self.neurossm_state_size,
            },
            "optimization": {
                "dtype": self.dtype,
                "mixed_precision": self.mixed_precision,
                "gradient_checkpointing": self.gradient_checkpointing,
                "memory_efficient_attention": self.memory_efficient_attention,
                "fast_mode": self.fast_mode,
            },
            "device": {
                "device": self.device,
                "use_cuda": self.use_cuda,
            }
        }
    
    def print_summary(self):
        ""
        summary = self.summary()
        
        print("=" * 60)
        print("NEURATENSOR MODEL CONFIGURATION")
        print("=" * 60)
        
        print("\nModel Architecture:")
        for key, value in summary["architecture"].items():
            print(f"  {key:25s}: {value:,}")
        
        print("\nSNN Configuration:")
        for key, value in summary["snn"].items():
            print(f"  {key:25s}: {value:,}")
        
        print("\nNeuroSSM Configuration:")
        for key, value in summary["ssm"].items():
            print(f"  {key:25s}: {value:,}")
        
        print("\nOptimization Settings:")
        for key, value in summary["optimization"].items():
            print(f"  {key:25s}: {value}")
        
        print("\nDevice Settings:")
        for key, value in summary["device"].items():
            print(f"  {key:25s}: {value}")
        
        print("=" * 60)

@dataclass
class JetsonOrinConfig(ModelConfig):
    ""

    power_optimization: bool = True
    target_power_mode: str = "MAXN"
    thermal_monitoring: bool = True
    thermal_throttle_temp: float = 85.0

    max_memory_usage_mb: int = 16000
    cache_clear_interval: int = 5
    
    def __post_init__(self):
        ""
        super().__post_init__()
        self._validate_jetson()
    
    def _validate_jetson(self):
        ""

        valid_power_modes = ["MAXN", "15W", "30W", "50W"]
        if self.target_power_mode not in valid_power_modes:
            raise ValueError(f"target_power_mode must be one of {valid_power_modes}, got {self.target_power_mode}")

        if self.thermal_throttle_temp <= 0 or self.thermal_throttle_temp > 100:
            raise ValueError(f"thermal_throttle_temp must be between 0 and 100°C, got {self.thermal_throttle_temp}")

        if self.max_memory_usage_mb <= 0:
            raise ValueError(f"max_memory_usage_mb must be positive, got {self.max_memory_usage_mb}")
        
        if self.cache_clear_interval <= 0:
            raise ValueError(f"cache_clear_interval must be positive, got {self.cache_clear_interval}")

