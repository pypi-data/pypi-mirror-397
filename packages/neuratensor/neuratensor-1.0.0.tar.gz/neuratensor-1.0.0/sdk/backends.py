"""
Hardware Backend Detection
==========================

Auto-detection and management of hardware backends.
"""

import torch
import platform
from typing import Optional
from .config import Backend


class HardwareBackend:
    """Base class for hardware backends"""
    
    def __init__(self, name: str):
        self.name = name
        self.device_name = None
        self.compute_capability = None
        self.available = False
    
    def detect(self) -> bool:
        """Detect if backend is available"""
        raise NotImplementedError
    
    def optimize(self):
        """Apply backend-specific optimizations"""
        pass
    
    def __repr__(self):
        return f"{self.name}(available={self.available})"


class JetsonOrinBackend(HardwareBackend):
    """NVIDIA Jetson Orin backend"""
    
    def __init__(self):
        super().__init__("jetson_orin")
    
    def detect(self) -> bool:
        """Detect Jetson Orin"""
        if not torch.cuda.is_available():
            return False
        
        # Check device name
        device_name = torch.cuda.get_device_name(0)
        self.device_name = device_name
        
        # Jetson Orin has "Orin" in name and SM 8.7
        if "Orin" in device_name:
            props = torch.cuda.get_device_properties(0)
            self.compute_capability = f"{props.major}.{props.minor}"
            self.available = self.compute_capability == "8.7"
            return self.available
        
        return False
    
    def optimize(self):
        """Optimize for Jetson Orin"""
        if torch.cuda.is_available():
            # Enable TF32 for Ampere
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Enable cudnn benchmarking
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False


class JetsonAGXBackend(HardwareBackend):
    """NVIDIA Jetson AGX Xavier backend"""
    
    def __init__(self):
        super().__init__("jetson_agx")
    
    def detect(self) -> bool:
        """Detect Jetson AGX Xavier"""
        if not torch.cuda.is_available():
            return False
        
        device_name = torch.cuda.get_device_name(0)
        self.device_name = device_name
        
        if "Xavier" in device_name:
            props = torch.cuda.get_device_properties(0)
            self.compute_capability = f"{props.major}.{props.minor}"
            self.available = True
            return True
        
        return False


class NvidiaDesktopBackend(HardwareBackend):
    """NVIDIA Desktop GPU backend (RTX, GTX, Tesla)"""
    
    def __init__(self):
        super().__init__("nvidia_desktop")
    
    def detect(self) -> bool:
        """Detect desktop NVIDIA GPU"""
        if not torch.cuda.is_available():
            return False
        
        device_name = torch.cuda.get_device_name(0)
        self.device_name = device_name
        
        # Desktop cards
        desktop_keywords = ["RTX", "GTX", "Tesla", "Quadro", "TITAN", "A100", "H100"]
        
        for keyword in desktop_keywords:
            if keyword in device_name:
                props = torch.cuda.get_device_properties(0)
                self.compute_capability = f"{props.major}.{props.minor}"
                self.available = True
                return True
        
        return False
    
    def optimize(self):
        """Optimize for desktop GPU"""
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            
            # Enable TF32 for Ampere and newer (SM >= 8.0)
            if props.major >= 8:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
            
            torch.backends.cudnn.benchmark = True


class CUDAGenericBackend(HardwareBackend):
    """Generic CUDA backend (fallback)"""
    
    def __init__(self):
        super().__init__("cuda_generic")
    
    def detect(self) -> bool:
        """Detect any CUDA device"""
        if torch.cuda.is_available():
            self.device_name = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            self.compute_capability = f"{props.major}.{props.minor}"
            self.available = True
            return True
        return False


def detect_backend() -> HardwareBackend:
    """
    Auto-detect best available hardware backend.
    
    Returns:
        Detected backend instance
    
    Example:
        >>> backend = detect_backend()
        >>> print(f"Detected: {backend.name}")
    """
    # Try backends in priority order
    backends = [
        JetsonOrinBackend(),
        JetsonAGXBackend(),
        NvidiaDesktopBackend(),
        CUDAGenericBackend(),
    ]
    
    for backend in backends:
        if backend.detect():
            return backend
    
    # No CUDA available
    generic = HardwareBackend("cpu")
    generic.available = True
    return generic


def get_backend(backend_type: Backend) -> HardwareBackend:
    """
    Get specific backend or auto-detect.
    
    Args:
        backend_type: Backend enum value
    
    Returns:
        Backend instance
    """
    if backend_type == Backend.AUTO:
        return detect_backend()
    
    backend_map = {
        Backend.JETSON_ORIN: JetsonOrinBackend(),
        Backend.JETSON_AGX: JetsonAGXBackend(),
        Backend.NVIDIA_DESKTOP: NvidiaDesktopBackend(),
        Backend.CUDA_GENERIC: CUDAGenericBackend(),
    }
    
    backend = backend_map.get(backend_type)
    if backend and backend.detect():
        return backend
    
    raise RuntimeError(f"Backend {backend_type} not available")


def print_backend_info():
    """Print information about detected backend"""
    backend = detect_backend()
    
    print("=" * 60)
    print("NEURATENSOR BACKEND INFORMATION")
    print("=" * 60)
    print(f"Backend:             {backend.name}")
    print(f"Available:           {backend.available}")
    
    if backend.device_name:
        print(f"Device:              {backend.device_name}")
    
    if backend.compute_capability:
        print(f"Compute Capability:  {backend.compute_capability}")
    
    if torch.cuda.is_available():
        print(f"CUDA Version:        {torch.version.cuda}")
        print(f"PyTorch Version:     {torch.__version__}")
        props = torch.cuda.get_device_properties(0)
        print(f"Total Memory:        {props.total_memory / 1024**3:.1f} GB")
    
    print("=" * 60)
