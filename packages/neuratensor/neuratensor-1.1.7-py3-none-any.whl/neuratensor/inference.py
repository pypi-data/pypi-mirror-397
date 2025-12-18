"""
NeuraTensor Inference Engine
=============================

High-level inference API wrapping the proprietary core.
"""

import torch
import torch.nn as nn
from typing import Optional, Union, Dict, Any, List
from pathlib import Path
import sys

# Add paths for core imports
current_dir = Path(__file__).parent
neuratensor_dir = current_dir.parent
if str(neuratensor_dir) not in sys.path:
    sys.path.insert(0, str(neuratensor_dir))

from core.model import NeuraTensorModel
from config.presets import create_64m_config, create_256m_config, create_1b_config
from .config import SDKConfig, InferenceConfig, ModelSize, Backend
from .backends import get_backend


class NeuraTensor:
    """
    NeuraTensor - High-Performance Neuromorphic Inference
    
    Public API for neuromorphic tensor processing. Uses proprietary
    CUDA kernels for optimal performance.
    
    Example:
        >>> model = NeuraTensor.from_pretrained("64m")
        >>> output = model(input_ids)
        >>> tokens = model.generate(prompt, max_tokens=50)
    """
    
    def __init__(self, config: Optional[SDKConfig] = None):
        """
        Initialize NeuraTensor model.
        
        Args:
            config: SDK configuration (uses defaults if None)
        """
        self.config = config or SDKConfig()
        self._backend = None
        self._model = None
        self._device = None
        self._initialized = False
    
    def _initialize(self):
        """Initialize model and backend"""
        if self._initialized:
            return
        
        # Get backend
        self._backend = get_backend(self.config.backend)
        
        # Create internal config based on model size
        if self.config.model_size == ModelSize.M64:
            internal_config = create_64m_config()
        elif self.config.model_size == ModelSize.M256:
            internal_config = create_256m_config()
        elif self.config.model_size == ModelSize.B1:
            internal_config = create_1b_config()
        else:
            raise ValueError(f"Unknown model size: {self.config.model_size}")
        
        # Override with SDK config
        internal_config.max_sequence_length = self.config.max_sequence_length
        internal_config.dtype = self.config.precision.value.replace("float", "float")
        
        # Setup device
        self._device = torch.device(self.config.device if torch.cuda.is_available() else "cpu")
        internal_config.device = str(self._device)
        internal_config.use_cuda = self._device.type == "cuda"
        
        # Create model
        self._model = NeuraTensorModel(internal_config)
        self._model.to(self._device)
        
        # Apply precision
        if self.config.precision == "float16":
            self._model = self._model.half()
        
        self._model.eval()
        self._initialized = True
    
    @classmethod
    def from_pretrained(
        cls,
        model_name: str,
        backend: str = "auto",
        device: str = "cuda",
        **kwargs
    ) -> 'NeuraTensor':
        """
        Load pretrained NeuraTensor model.
        
        Args:
            model_name: Model identifier ('64m', '256m', '1b')
            backend: Hardware backend
            device: Device to load on
            **kwargs: Additional config parameters
        
        Returns:
            Initialized NeuraTensor instance
        
        Example:
            >>> model = NeuraTensor.from_pretrained("64m")
            >>> model = NeuraTensor.from_pretrained("256m", device="cuda:1")
        """
        config = SDKConfig(
            model_size=model_name,
            backend=backend,
            device=device,
            **kwargs
        )
        
        instance = cls(config)
        instance._initialize()
        return instance
    
    def __call__(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        return_dict: bool = True
    ) -> Union[torch.Tensor, Dict[str, Any]]:
        """
        Run inference on input tokens.
        
        Args:
            input_ids: Input token IDs [batch, seq_len]
            attention_mask: Attention mask (optional)
            return_dict: Return dictionary instead of tensor
        
        Returns:
            Logits tensor or dictionary with outputs
        
        Example:
            >>> input_ids = torch.randint(0, 50000, (1, 64))
            >>> output = model(input_ids)
        """
        if not self._initialized:
            self._initialize()
        
        # Move to device
        input_ids = input_ids.to(self._device)
        
        # Validate batch size
        if input_ids.size(0) > self.config.batch_size:
            raise ValueError(
                f"Input batch size {input_ids.size(0)} exceeds "
                f"configured batch_size {self.config.batch_size}"
            )
        
        # Run inference
        with torch.no_grad():
            outputs = self._model(input_ids)
        
        if return_dict:
            return outputs
        else:
            return outputs['logits']
    
    def generate(
        self,
        prompt: Union[str, torch.Tensor],
        max_new_tokens: int = 50,
        inference_config: Optional[InferenceConfig] = None,
        tokenizer = None
    ) -> Union[torch.Tensor, str]:
        """
        Generate tokens from prompt.
        
        Args:
            prompt: Input prompt (string if tokenizer provided)
            max_new_tokens: Number of tokens to generate
            inference_config: Inference parameters
            tokenizer: Optional tokenizer for string input/output
        
        Returns:
            Generated tokens or decoded string
        
        Example:
            >>> tokens = model.generate(input_ids, max_new_tokens=100)
        """
        if not self._initialized:
            self._initialize()
        
        inference_config = inference_config or InferenceConfig()
        
        # Handle string input
        if isinstance(prompt, str):
            if tokenizer is None:
                raise ValueError("tokenizer required for string input")
            input_ids = tokenizer.encode(prompt, return_tensors="pt")
        else:
            input_ids = prompt
        
        input_ids = input_ids.to(self._device)
        
        # Generate tokens
        generated = input_ids
        
        for _ in range(max_new_tokens):
            # Get logits for last token
            outputs = self(generated)
            next_token_logits = outputs['logits'][:, -1, :]
            
            # Apply temperature
            if inference_config.temperature > 0:
                next_token_logits = next_token_logits / inference_config.temperature
            
            # Sample or greedy
            if inference_config.do_sample:
                probs = torch.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
            else:
                next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            
            # Append token
            generated = torch.cat([generated, next_token], dim=1)
            
            # Check max length
            if generated.size(1) >= self.config.max_sequence_length:
                break
        
        # Decode if tokenizer provided
        if tokenizer is not None:
            return tokenizer.decode(generated[0], skip_special_tokens=True)
        
        return generated
    
    def benchmark(self, num_iterations: int = 100) -> Dict[str, float]:
        """
        Run performance benchmark.
        
        Args:
            num_iterations: Number of iterations
        
        Returns:
            Dictionary with performance metrics
        
        Example:
            >>> results = model.benchmark()
            >>> print(f"Latency: {results['mean_latency_ms']:.2f}ms")
        """
        if not self._initialized:
            self._initialize()
        
        # Create dummy input
        input_ids = torch.randint(
            0, 50000,
            (self.config.batch_size, self.config.max_sequence_length),
            device=self._device
        )
        
        # Warmup
        for _ in range(10):
            _ = self(input_ids)
        
        # Benchmark
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        
        import time
        times = []
        
        for _ in range(num_iterations):
            start = time.perf_counter()
            _ = self(input_ids)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        import numpy as np
        times = np.array(times)
        
        return {
            'mean_latency_ms': float(times.mean()),
            'std_latency_ms': float(times.std()),
            'min_latency_ms': float(times.min()),
            'max_latency_ms': float(times.max()),
            'throughput_seq_per_sec': float(1000 / times.mean()),
            'num_iterations': num_iterations,
            'batch_size': self.config.batch_size,
            'sequence_length': self.config.max_sequence_length,
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.
        
        Returns:
            Dictionary with model metadata
        """
        if not self._initialized:
            self._initialize()
        
        return {
            'model_size': self.config.model_size.value,
            'parameters': self._model.count_parameters(),
            'backend': self.config.backend.value,
            'precision': self.config.precision.value,
            'device': str(self._device),
            'max_sequence_length': self.config.max_sequence_length,
            'batch_size': self.config.batch_size,
        }
    
    def __repr__(self) -> str:
        return (
            f"NeuraTensor(\n"
            f"  model_size={self.config.model_size.value},\n"
            f"  backend={self.config.backend.value},\n"
            f"  device={self.config.device},\n"
            f"  initialized={self._initialized}\n"
            f")"
        )
