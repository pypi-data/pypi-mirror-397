# NeuraTensor SDK

**Production neuromorphic inference at 8ms latency**

NeuraTensor is a high-performance neuromorphic inference runtime featuring a proprietary fused SNN-SSM architecture with CUDA acceleration. Optimized for NVIDIA Jetson AGX Orin and edge deployment.

[![PyPI version](https://badge.fury.io/py/neuratensor.svg)](https://pypi.org/project/neuratensor/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CUDA 11.4+](https://img.shields.io/badge/cuda-11.4+-green.svg)](https://developer.nvidia.com/cuda-downloads)

---

## ⚡ Performance

- **8.13ms mean latency** (Jetson AGX Orin, batch=1, seq=64, FP16)
- **123 sequences/sec throughput**
- **Sub-10ms** real-time inference guarantee
- **Up to 120× lower latency** vs standard PyTorch execution (measured on Jetson AGX Orin, batch=1, seq=64, same model architecture)

---

## 🚀 Quick Start

### Installation

```bash
pip install neuratensor
```

### Python API

```python
from neuratensor import NeuraTensor, NeuraTensorConfig
import torch

# Load model (3 lines)
config = NeuraTensorConfig.preset("64m")
model = NeuraTensor(config).cuda().half()

# Inference (1 line)
input_ids = torch.randint(0, 50000, (1, 64), device="cuda")
output = model(input_ids)
# ✅ 8ms latency, 64M params, 123 seq/s
```

### CLI Benchmark

```bash
# Run benchmark
neuratensor benchmark 64m --iterations 100

# Example output:
# ============================================================
# NeuraTensor 64M | Benchmark
# ============================================================
# Device:    Orin (SM 8.7)
# CUDA:      11.4
# ------------------------------------------------------------
# Latency (mean):    8.13 ms ± 0.07 ms
# Latency (p99):     8.22 ms
# Throughput:        123.0 seq/s
# Kernel:            fused_snn_ssm (secure)
# ============================================================
```

---

## 🏗️ Architecture

- **Hybrid SNN-SSM**: 6 spiking layers + 10 state space layers
- **Fused CUDA kernels**: Single-pass execution (patent pending)
- **FP16 optimized**: Hardware tensor cores
- **Deterministic latency**: No dynamic dispatch overhead

---

## 📦 Available Models

| Model | Parameters | Latency (Orin) | Throughput | Use Case |
|-------|-----------|----------------|------------|----------|
| 64M   | 64,155,526 | 8.13ms | 123 seq/s | Edge, real-time |
| 256M  | 256M | ~15ms | 67 seq/s | Balanced |
| 1B    | 1B | ~35ms | 29 seq/s | Quality |

*All measurements: Jetson AGX Orin, batch=1, seq=64, FP16*

---

## ⚠️ What This Is NOT

NeuraTensor is **NOT**:
- ❌ A training framework
- ❌ A general-purpose Transformer library  
- ❌ A drop-in replacement for PyTorch
- ❌ An autograd-enabled tensor library

NeuraTensor **IS**:
- ✅ A production-grade inference runtime
- ✅ Optimized for edge latency and determinism
- ✅ Purpose-built for neuromorphic architectures
- ✅ A compiled binary SDK with Python bindings

---

## 💻 Supported Hardware

### Tested & Validated:
- ✅ **Jetson AGX Orin** (primary target)
- ✅ **Jetson Orin NX**
- ✅ **Jetson Orin Nano** (limited testing)

### Experimental Support:
- ⚠️ **NVIDIA RTX 30xx / 40xx** (desktop GPUs)
- ⚠️ **A100, H100** (datacenter GPUs)

### Requirements:
- **CUDA Compute Capability**: 7.0 or higher (SM 7.0+)
- **CUDA Toolkit**: 11.4 or higher
- **Driver**: 470.x or higher
- **Python**: 3.8, 3.9, 3.10
- **PyTorch**: 2.0+ (for tensor compatibility only)

**Note**: If your GPU is unsupported, the SDK will raise a clear error at import time. Source code for the core runtime is not distributed.

---

## 📦 Binary Distribution Model

The SDK ships with **precompiled CUDA binaries** for maximum performance:

- ✅ Optimized for Jetson AGX Orin (ARM64 + CUDA 11.4)
- ✅ No compilation required at install time
- ✅ Symbols obfuscated for IP protection
- ⚠️ Platform-specific (Linux ARM64 only for v1.x)

If your system configuration is unsupported, you will see:
```
RuntimeError: CUDA kernel not compatible with this device
```

**Source code for the proprietary core is not distributed.** Binary-only distribution is intentional.

---

## 🔒 Security & IP Notice

NeuraTensor contains **proprietary CUDA kernels and runtime logic** protected by:

- **Patent-pending architecture** (USPTO filing: pending)
- **Obfuscated binaries** (symbols stripped and renamed)
- **Restricted license** (see [PATENT_NOTICE.txt](https://pypi.org/project/neuratensor/))

**Reverse engineering, redistribution, or modification of the core binaries is prohibited by the license.**

For commercial licensing, custom hardware support, or source code access:
- Email: licensing@neuramorphic.ai
- Website: https://neuramorphic.ai

---

## 🔧 Requirements

### System:
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Architecture**: ARM64 (Jetson) or x86_64 (experimental)
- **CUDA**: 11.4+ with cuDNN
- **GPU Memory**: 2GB minimum

### Python:
```bash
pip install neuratensor

# Dependencies (auto-installed):
# - torch >= 2.0.0
# - numpy >= 1.19.0
```

---

## 📚 Documentation

- **Quick Start**: [examples/](https://github.com/neuramorphic/neuratensor-sdk)
- **API Reference**: Coming soon
- **Performance Guide**: Coming soon
- **Hardware Guide**: Coming soon

---

## 🤝 Support

### Community:
- **GitHub Issues**: For bugs and feature requests (repo link TBD)
- **PyPI Page**: https://pypi.org/project/neuratensor/

### Enterprise:
- **Custom Models**: enterprise@neuramorphic.ai
- **Licensing**: licensing@neuramorphic.ai
- **NVIDIA Partners**: partners@neuramorphic.ai

---

## 📊 Citation

If you use NeuraTensor in your research or product, please cite:

```bibtex
@software{neuratensor2025,
  title = {NeuraTensor: High-Performance Neuromorphic Inference SDK},
  author = {Neuramorphic, Inc.},
  year = {2025},
  url = {https://pypi.org/project/neuratensor/}
}
```

---

## 📄 License

**Proprietary License** - Binary distribution only.

- ✅ Evaluation and non-commercial use permitted
- ⚠️ Commercial use requires separate license agreement
- ❌ Reverse engineering strictly prohibited
- ❌ Redistribution not permitted

See [LICENSE](LICENSE) and [PATENT_NOTICE.txt](PATENT_NOTICE.txt) for details.

---

## 🏢 About

NeuraTensor is developed by [Neuramorphic, Inc.](https://neuramorphic.ai)

**Patent-pending neuromorphic architecture** combining spiking neural networks with state space models for ultra-low latency inference on edge devices.

---

**© 2024-2025 Neuramorphic, Inc. All rights reserved.**
