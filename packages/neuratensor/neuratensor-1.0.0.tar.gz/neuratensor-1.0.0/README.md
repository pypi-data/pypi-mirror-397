# NeuraTensor SDK

**Production neuromorphic inference at 8ms latency**

NeuraTensor is a high-performance neuromorphic inference SDK featuring a proprietary fused SNN-SSM architecture with CUDA acceleration.

## ⚡ Performance

- **8.13ms latency** (64M model, Jetson AGX Orin)
- **123 seq/s throughput**
- **120x faster** than PyTorch baseline
- Sub-10ms real-time inference

## �� Quick Start

```bash
pip install neuratensor
```

```python
from neuratensor import NeuraTensor, NeuraTensorConfig

# Load model
config = NeuraTensorConfig.preset("64m")
model = NeuraTensor(config).cuda().half()

# Inference
output = model(input_ids)
# ✅ 8ms latency, 64M params, 123 seq/s
```

## 📊 Models

| Model | Parameters | Latency | Use Case |
|-------|-----------|---------|----------|
| 64M   | 64M | 8ms | Edge, real-time |
| 256M  | 256M | ~15ms | Balanced |
| 1B    | 1B | ~35ms | Quality |

## 🔧 Requirements

- NVIDIA GPU (CUDA 11.4+, SM 7.0+)
- Python 3.8+
- PyTorch 2.0+

## 📚 Documentation

- [Distribution Guide](DISTRIBUTION_GUIDE.md)
- [Patent Notice](PATENT_NOTICE.txt)

## 📄 License

Proprietary. Binary distribution only.

**© 2024-2025 Neuramorphic, Inc.**
