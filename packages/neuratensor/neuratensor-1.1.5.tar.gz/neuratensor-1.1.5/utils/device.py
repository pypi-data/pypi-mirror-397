"""
Device Utilities
================

Device detection and management.
"""

import torch
import subprocess
from typing import Dict, Any, Optional


def check_cuda_available() -> bool:
    """Check if CUDA is available"""
    return torch.cuda.is_available()


def get_device_info() -> Dict[str, Any]:
    """
    Get detailed device information.
    
    Returns:
        Dictionary with device details
    """
    info = {
        'cuda_available': torch.cuda.is_available(),
        'cuda_version': None,
        'device_count': 0,
        'device_name': None,
        'compute_capability': None,
        'total_memory_gb': 0.0,
        'jetson_model': None,
    }
    
    if not torch.cuda.is_available():
        return info
    
    # CUDA info
    info['cuda_version'] = torch.version.cuda
    info['device_count'] = torch.cuda.device_count()
    
    if info['device_count'] > 0:
        device = torch.cuda.current_device()
        info['device_name'] = torch.cuda.get_device_name(device)
        
        # Memory
        total_memory = torch.cuda.get_device_properties(device).total_memory
        info['total_memory_gb'] = total_memory / (1024**3)
        
        # Compute capability
        props = torch.cuda.get_device_properties(device)
        info['compute_capability'] = f"{props.major}.{props.minor}"
    
    # Detect Jetson model
    try:
        result = subprocess.run(
            ['cat', '/proc/device-tree/model'],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0:
            model = result.stdout.strip()
            if 'Jetson' in model or 'Orin' in model:
                info['jetson_model'] = model
    except Exception:
        pass
    
    return info


def print_device_info():
    """Print formatted device information"""
    info = get_device_info()
    
    print("=" * 60)
    print("DEVICE INFORMATION")
    print("=" * 60)
    print(f"CUDA Available:      {info['cuda_available']}")
    
    if info['cuda_available']:
        print(f"CUDA Version:        {info['cuda_version']}")
        print(f"Device Count:        {info['device_count']}")
        print(f"Device Name:         {info['device_name']}")
        print(f"Compute Capability:  {info['compute_capability']}")
        print(f"Total Memory:        {info['total_memory_gb']:.1f} GB")
        
        if info['jetson_model']:
            print(f"Jetson Model:        {info['jetson_model']}")
    
    print("=" * 60)


def set_device(device_id: int = 0) -> torch.device:
    """
    Set and return CUDA device.
    
    Args:
        device_id: CUDA device ID
    
    Returns:
        torch.device
    """
    if not torch.cuda.is_available():
        return torch.device('cpu')
    
    torch.cuda.set_device(device_id)
    return torch.device(f'cuda:{device_id}')


def optimize_cuda():
    """Enable CUDA optimizations"""
    if not torch.cuda.is_available():
        return
    
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
