"""
NeuraTensor Core Module - Proprietary
=====================================
This code is obfuscated and proprietary.
Reverse engineering is prohibited.
© 2024-2025 Neuramorphic, Inc.
"""
""

import torch
import torch.nn as nn
import sys
from pathlib import Path
from typing import Dict, Any

current_dir = Path(__file__).parent
neuratensor_dir = current_dir.parent
if str(neuratensor_dir) not in sys.path:
    sys.path.insert(0, str(neuratensor_dir))

from core.fused_layer import FusedSNNSSMLayer
from config.model_config import ModelConfig
from utils.logger import get_logger

logger = get_logger("neuratensor.model")

class NeuraTensorModel(nn.Module):
    ""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        
        if not isinstance(config, ModelConfig):
            raise TypeError(f"config must be ModelConfig, got {type(config)}")
        
        self.config = config
        self.vocab_size = config.vocab_size
        self.hidden_size = config.hidden_size
        self.state_size = config.neurossm_state_size
        self.num_layers = config.snn_layers

        self.embedding = nn.Embedding(self.vocab_size, self.hidden_size)

        self.layers = nn.ModuleList([
            FusedSNNSSMLayer(
                hidden_size=self.hidden_size,
                state_size=self.state_size,
                use_cuda=config.use_cuda
            )
            for _ in range(self.num_layers)
        ])

        self.output_proj = nn.Linear(self.hidden_size, self.vocab_size, bias=False)

        self.output_proj.weight = self.embedding.weight

        self._init_weights()
        
        logger.info(f"NeuraTensorModel initialized: {self.count_parameters():,} parameters")
    
    def _init_weights(self):
        ""
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.02)
    
    def forward(self, input_ids: torch.Tensor) -> Dict[str, Any]:
        ""
        if not isinstance(input_ids, torch.Tensor):
            raise TypeError(f"input_ids must be torch.Tensor, got {type(input_ids)}")
        
        if input_ids.dim() != 2:
            raise ValueError(f"input_ids must be 2D [batch, seq], got shape {input_ids.shape}")

        x = self.embedding(input_ids)

        for layer in self.layers:
            x = layer(x)

        logits = self.output_proj(x)

        return {
            'logits': logits,
            'snn_metrics': {
                'metrics': {
                    'total_spikes': 0,
                    'functional_layers': self.num_layers,
                    'variability_metrics': [1.0] * self.num_layers
                }
            }
        }
    
    def count_parameters(self) -> int:
        ""
        return sum(p.numel() for p in self.parameters())
    
    def get_model_info(self) -> Dict[str, Any]:
        ""
        return {
            'total_parameters': self.count_parameters(),
            'hidden_size': self.hidden_size,
            'state_size': self.state_size,
            'num_layers': self.num_layers,
            'vocab_size': self.vocab_size,
            'model_type': 'NeuraTensorModel'
        }
    
    def print_model_info(self):
        ""
        info = self.get_model_info()
        
        print("=" * 60)
        print("NEURATENSOR MODEL INFO")
        print("=" * 60)
        print(f"Model Type:        {info['model_type']}")
        print(f"Total Parameters:  {info['total_parameters']:,}")
        print(f"Hidden Size:       {info['hidden_size']:,}")
        print(f"State Size:        {info['state_size']:,}")
        print(f"Num Layers:        {info['num_layers']}")
        print(f"Vocab Size:        {info['vocab_size']:,}")
        print("=" * 60)

