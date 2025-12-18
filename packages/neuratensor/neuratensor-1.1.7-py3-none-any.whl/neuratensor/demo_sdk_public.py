#!/usr/bin/env python3
"""
NeuraTensor SDK Demo - Canonical Public Example
================================================

This is the OFFICIAL demo for NeuraTensor SDK users.
Uses ONLY public SDK API - no internal imports.

Run:
    python demo_sdk_public.py
"""

import torch
from pathlib import Path
import sys

# Add neuratensor to path
neuratensor_dir = Path(__file__).parent.parent
sys.path.insert(0, str(neuratensor_dir))

print("=" * 60)
print("NeuraTensor SDK - Public Demo")
print("=" * 60)

# Step 1: Import SDK (PUBLIC API ONLY)
print("\n1️⃣  Importing NeuraTensor SDK...")
from sdk import NeuraTensor, NeuraTensorConfig

print("   ✅ SDK imported")

# Step 2: Create configuration from preset
print("\n2️⃣  Loading 64M preset configuration...")
config = NeuraTensorConfig.preset("64m")

print(f"   ✅ Config loaded:")
print(f"      - Model: {config.model_size.value}")
print(f"      - Vocab: {config.vocab_size:,}")
print(f"      - Hidden: {config.hidden_size}")
print(f"      - Max seq: {config.max_sequence_length}")

# Step 3: Create model
print("\n3️⃣  Creating NeuraTensor model...")
model = NeuraTensor(config).cuda().half()

print(f"   ✅ Model created: {model.count_parameters():,} parameters")

# Step 4: Prepare input
print("\n4️⃣  Preparing input tensor...")
input_ids = torch.randint(
    0, 
    config.vocab_size, 
    (1, config.max_sequence_length),
    device="cuda"
)

print(f"   ✅ Input shape: {input_ids.shape}")

# Step 5: Run inference
print("\n5️⃣  Running inference...")
with torch.no_grad():
    # Warmup
    for _ in range(2):
        _ = model(input_ids)
        torch.cuda.synchronize()
    
    # Timed inference
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    
    start.record()
    output = model(input_ids)
    end.record()
    
    torch.cuda.synchronize()
    latency = start.elapsed_time(end)

print(f"   ✅ Output shape: {output['logits'].shape}")
print(f"   ✅ Latency: {latency:.2f}ms")

# Step 6: Summary
print("\n" + "=" * 60)
print("✅ Demo Complete!")
print("=" * 60)
print(f"Model:      {config.model_size.value.upper()} ({model.count_parameters():,} params)")
print(f"Latency:    {latency:.2f}ms")
print(f"Throughput: {1000/latency:.2f} seq/sec")
print(f"Device:     {torch.cuda.get_device_name(0)}")
print("=" * 60)

print("\n📖 This demo uses ONLY the public SDK API:")
print("   - from sdk import NeuraTensor, NeuraTensorConfig")
print("   - config = NeuraTensorConfig.preset('64m')")
print("   - model = NeuraTensor(config)")
print("\n✅ No internal imports needed!")
