"""
Test Inference Engine
=====================

Tests for InferenceEngine functionality.
"""

import pytest
import torch
from neuratensor_sdk import NeuraTensor
from neuratensor_sdk.inference import InferenceEngine


@pytest.fixture
def model():
    """Create a test model"""
    return NeuraTensor.from_config("64m")


@pytest.fixture
def engine(model):
    """Create inference engine"""
    return InferenceEngine(model)


def test_single_inference(engine):
    """Test single inference call"""
    input_ids = torch.randint(0, 50000, (1, 64))
    result = engine.infer(input_ids)
    
    assert "logits" in result
    assert result["logits"].shape == (1, 64, 50000)
    assert "latency_ms" in result
    assert result["latency_ms"] > 0


def test_batch_inference(engine):
    """Test batch inference"""
    input_ids = torch.randint(0, 50000, (4, 64))
    result = engine.infer_batch(input_ids)
    
    assert len(result) == 4
    for r in result:
        assert "logits" in r
        assert r["logits"].shape == (1, 64, 50000)


def test_benchmark(engine):
    """Test benchmark functionality"""
    results = engine.benchmark(
        batch_size=1,
        seq_length=64,
        num_iterations=10,
        warmup_iterations=2
    )
    
    assert "mean_latency_ms" in results
    assert "std_latency_ms" in results
    assert "throughput_seq_per_sec" in results
    assert results["mean_latency_ms"] > 0


def test_cuda_inference(engine):
    """Test CUDA inference"""
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    
    engine.model.cuda()
    input_ids = torch.randint(0, 50000, (1, 64)).cuda()
    
    result = engine.infer(input_ids)
    assert result["logits"].is_cuda


@pytest.mark.parametrize("batch_size", [1, 2, 4, 8])
def test_different_batch_sizes(engine, batch_size):
    """Test different batch sizes"""
    input_ids = torch.randint(0, 50000, (batch_size, 64))
    results = engine.infer_batch(input_ids)
    
    assert len(results) == batch_size


@pytest.mark.parametrize("seq_length", [32, 64, 128])
def test_different_sequence_lengths(engine, seq_length):
    """Test different sequence lengths"""
    input_ids = torch.randint(0, 50000, (1, seq_length))
    result = engine.infer(input_ids)
    
    assert result["logits"].shape == (1, seq_length, 50000)
