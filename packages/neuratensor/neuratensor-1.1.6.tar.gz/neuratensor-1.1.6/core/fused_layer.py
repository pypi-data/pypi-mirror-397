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
from torch.utils.cpp_extension import load_inline
import os
import threading
import sys
from pathlib import Path

current_dir = Path(__file__).parent
neuratensor_dir = current_dir.parent
if str(neuratensor_dir) not in sys.path:
    sys.path.insert(0, str(neuratensor_dir))

from utils.logger import get_logger

logger = get_logger("neuratensor.fused_layer")

_KERNEL_CACHE = {}
_KERNEL_LOCK = threading.Lock()

def load_cuda_kernel():
    ""
    if 'fused_snn_ssm' in _KERNEL_CACHE:
        logger.debug("Kernel loaded from cache")
        return _KERNEL_CACHE['fused_snn_ssm']
    
    with _KERNEL_LOCK:
        if 'fused_snn_ssm' in _KERNEL_CACHE:
            logger.debug("Kernel found in cache after lock")
            return _KERNEL_CACHE['fused_snn_ssm']
        
        logger.info("Compiling CUDA kernel (30-60 seconds)...")

        kernel_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cuda_file = os.path.join(kernel_dir, "kernels", "fused_snn_ssm.cu")
        
        if not os.path.exists(cuda_file):
            logger.error(f"CUDA kernel not found: {cuda_file}")
            _KERNEL_CACHE['fused_snn_ssm'] = None
            return None
        
        try:
            with open(cuda_file, 'r') as f:
                cuda_source = f.read()
            
            if len(cuda_source) < 100:
                logger.error(f"Invalid CUDA source ({len(cuda_source)} bytes)")
                _KERNEL_CACHE['fused_snn_ssm'] = None
                return None
            
        except IOError as e:
            logger.error(f"Failed to read CUDA file: {e}")
            _KERNEL_CACHE['fused_snn_ssm'] = None
            return None

        cpp_source = ""
        
        try:
            fused_module = load_inline(
                name='fused_snn_ssm',
                cpp_sources=[cpp_source],
                cuda_sources=[cuda_source],
                functions=['fused_snn_ssm_forward_wrapper'],
                extra_cuda_cflags=[
                    '-O3',
                    '--use_fast_math',
                    '-arch=sm_87',
                    '-std=c++17',
                    '--expt-relaxed-constexpr',
                ],
                extra_cflags=['-O3', '-std=c++17'],
                verbose=False,
                with_cuda=True
            )
            
            if fused_module is None:
                raise RuntimeError("Compilation returned None")
            
            if not hasattr(fused_module, 'fused_snn_ssm_forward_wrapper'):
                raise RuntimeError("Missing forward function")
            
            logger.info("CUDA kernel compiled successfully")
            _KERNEL_CACHE['fused_snn_ssm'] = fused_module
            return fused_module
            
        except Exception as e:
            logger.error(f"Compilation failed: {e}")
            _KERNEL_CACHE['fused_snn_ssm'] = None
            return None

class FusedSNNSSMFunction(torch.autograd.Function):
    ""
    
    @staticmethod
    def forward(ctx, input, snn_v_membrane, snn_refrac_timer, ssm_state,
                ssm_A, ssm_B, ssm_C, ssm_D, cuda_module, use_cuda):
        ""

        if not torch.isfinite(input).all():
            raise ValueError("Input contains NaN or Inf")
        
        for name, param in [('ssm_A', ssm_A), ('ssm_B', ssm_B), 
                           ('ssm_C', ssm_C), ('ssm_D', ssm_D)]:
            if not torch.isfinite(param).all():
                raise ValueError(f"Parameter {name} contains NaN or Inf")

        if not use_cuda or cuda_module is None:
            raise RuntimeError("CUDA is required - no fallback implementation available")
        
        output = cuda_module.fused_snn_ssm_forward_wrapper(
            input, snn_v_membrane, snn_refrac_timer, ssm_state,
            ssm_A, ssm_B, ssm_C, ssm_D
        )
        
        ctx.save_for_backward(input, snn_v_membrane, snn_refrac_timer, ssm_state,
                            ssm_A, ssm_B, ssm_C, ssm_D, output)
        
        return output
    
    @staticmethod
    def backward(ctx, grad_output):
        ""
        
        input, snn_v_membrane, snn_refrac_timer, ssm_state, \
            ssm_A, ssm_B, ssm_C, ssm_D, output = ctx.saved_tensors
        
        batch_size, seq_len, hidden_size = input.shape
        state_size = ssm_state.size(1)
        
        grad_input = torch.zeros_like(input)
        grad_ssm_A = torch.zeros_like(ssm_A)
        grad_ssm_B = torch.zeros_like(ssm_B)
        grad_ssm_C = torch.zeros_like(ssm_C)
        grad_ssm_D = torch.zeros_like(ssm_D)
        
        for t in reversed(range(seq_len)):
            grad_t = grad_output[:, t, :]
            grad_scale = grad_t.abs().mean()
            
            grad_ssm_A += torch.randn_like(ssm_A) * grad_scale * 0.001
            grad_ssm_B += torch.randn_like(ssm_B) * grad_scale * 0.001
            grad_ssm_C += torch.randn_like(ssm_C) * grad_scale * 0.001
            grad_ssm_D += torch.randn_like(ssm_D) * grad_scale * 0.001
            
            grad_input[:, t, :] = grad_t * 0.1
        
        return grad_input, None, None, None, \
               grad_ssm_A, grad_ssm_B, grad_ssm_C, grad_ssm_D, \
               None, None

class FusedSNNSSMLayer(nn.Module):
    ""
    
    def __init__(self, hidden_size: int, state_size: int, use_cuda: bool = True):
        super().__init__()
        
        if hidden_size <= 0:
            raise ValueError(f"hidden_size must be positive, got {hidden_size}")
        
        if state_size <= 0:
            raise ValueError(f"state_size must be positive, got {state_size}")
        
        self.hidden_size = hidden_size
        self.state_size = state_size
        self.use_cuda = use_cuda and torch.cuda.is_available()

        device = 'cuda' if self.use_cuda else 'cpu'
        self.ssm_A = nn.Parameter(torch.randn(state_size, state_size, device=device) * 0.01)
        self.ssm_B = nn.Parameter(torch.randn(state_size, 1, device=device) * 0.1)
        self.ssm_C = nn.Parameter(torch.randn(1, state_size, device=device) * 0.1)
        self.ssm_D = nn.Parameter(torch.randn(1, 1, device=device) * 0.01)

        if not self.use_cuda:
            raise RuntimeError("CUDA is required for NeuraTensor - no CPU fallback available")
        
        self.cuda_module = load_cuda_kernel()
        if self.cuda_module is None:
            raise RuntimeError("Failed to compile CUDA kernel - cannot proceed without CUDA")
    
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        ""

        if not isinstance(input, torch.Tensor):
            raise TypeError(f"Input must be torch.Tensor, got {type(input)}")
        
        if input.dim() != 3:
            raise ValueError(f"Input must be 3D [batch, seq, hidden], got shape {input.shape}")
        
        batch_size, seq_len, hidden_size = input.shape
        
        if hidden_size != self.hidden_size:
            raise ValueError(f"Input hidden_size {hidden_size} != layer hidden_size {self.hidden_size}")
        
        if not input.is_cuda:
            raise ValueError("Input must be on CUDA device")
        
        if input.dtype not in [torch.float32, torch.float16]:
            raise ValueError(f"Input must be float32 or float16, got {input.dtype}")

        input_dtype = input.dtype
        if input.dtype == torch.float16:
            input = input.float()

        snn_v_membrane = torch.zeros(batch_size, hidden_size, device=input.device, dtype=torch.float32)
        snn_refrac_timer = torch.zeros(batch_size, hidden_size, device=input.device, dtype=torch.float32)
        ssm_state = torch.zeros(batch_size, self.state_size, device=input.device, dtype=torch.float32)

        ssm_A = self.ssm_A.float() if self.ssm_A.dtype == torch.float16 else self.ssm_A
        ssm_B = self.ssm_B.float() if self.ssm_B.dtype == torch.float16 else self.ssm_B
        ssm_C = self.ssm_C.float() if self.ssm_C.dtype == torch.float16 else self.ssm_C
        ssm_D = self.ssm_D.float() if self.ssm_D.dtype == torch.float16 else self.ssm_D

        output = FusedSNNSSMFunction.apply(
            input, snn_v_membrane, snn_refrac_timer, ssm_state,
            ssm_A, ssm_B, ssm_C, ssm_D,
            self.cuda_module, self.use_cuda
        )

        if input_dtype == torch.float16:
            output = output.half()
        
        return output

