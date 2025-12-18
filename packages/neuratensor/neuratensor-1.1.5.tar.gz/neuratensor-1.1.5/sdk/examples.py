"""
NeuraTensor SDK Examples
========================

Example scripts demonstrating SDK usage.
"""

import torch


def example_basic_inference():
    """Basic inference example"""
    print("=" * 70)
    print("Example 1: Basic Inference")
    print("=" * 70)
    
    from neuratensor.sdk import NeuraTensor
    
    # Load model
    print("\n1. Loading model...")
    model = NeuraTensor.from_pretrained("64m")
    
    # Create input
    print("2. Creating input...")
    input_ids = torch.randint(0, 50000, (1, 64))
    
    # Run inference
    print("3. Running inference...")
    output = model(input_ids)
    
    print(f"✓ Output shape: {output['logits'].shape}")
    print(f"✓ Output dtype: {output['logits'].dtype}")
    print()


def example_custom_config():
    """Custom configuration example"""
    print("=" * 70)
    print("Example 2: Custom Configuration")
    print("=" * 70)
    
    from neuratensor.sdk import NeuraTensor, SDKConfig
    
    # Create custom config
    print("\n1. Creating custom config...")
    config = SDKConfig(
        model_size="64m",
        backend="auto",
        precision="float16",
        batch_size=4,
        max_sequence_length=128,
        device="cuda"
    )
    
    print(f"   Model: {config.model_size.value}")
    print(f"   Batch: {config.batch_size}")
    print(f"   SeqLen: {config.max_sequence_length}")
    
    # Load model with config
    print("\n2. Loading model...")
    model = NeuraTensor(config)
    
    # Run inference with batch
    print("3. Running batch inference...")
    input_ids = torch.randint(0, 50000, (4, 128))
    output = model(input_ids)
    
    print(f"✓ Batch output shape: {output['logits'].shape}")
    print()


def example_generation():
    """Token generation example"""
    print("=" * 70)
    print("Example 3: Token Generation")
    print("=" * 70)
    
    from neuratensor.sdk import NeuraTensor, InferenceConfig
    
    # Load model
    print("\n1. Loading model...")
    model = NeuraTensor.from_pretrained("64m")
    
    # Create prompt
    print("2. Creating prompt...")
    prompt = torch.randint(0, 50000, (1, 10))
    
    # Configure generation
    inference_config = InferenceConfig(
        temperature=0.8,
        top_k=50,
        top_p=0.95,
        max_new_tokens=50,
        do_sample=True
    )
    
    # Generate
    print("3. Generating tokens...")
    generated = model.generate(
        prompt=prompt,
        max_new_tokens=50,
        inference_config=inference_config
    )
    
    print(f"✓ Generated shape: {generated.shape}")
    print(f"✓ Original length: {prompt.size(1)}")
    print(f"✓ Final length: {generated.size(1)}")
    print()


def example_benchmark():
    """Benchmark example"""
    print("=" * 70)
    print("Example 4: Performance Benchmark")
    print("=" * 70)
    
    from neuratensor.sdk import NeuraTensor
    
    # Load model
    print("\n1. Loading model...")
    model = NeuraTensor.from_pretrained("64m")
    
    # Run benchmark
    print("2. Running benchmark (100 iterations)...")
    results = model.benchmark(num_iterations=100)
    
    print("\nResults:")
    print(f"  Mean Latency:    {results['mean_latency_ms']:.2f}ms ± {results['std_latency_ms']:.2f}ms")
    print(f"  Min Latency:     {results['min_latency_ms']:.2f}ms")
    print(f"  Max Latency:     {results['max_latency_ms']:.2f}ms")
    print(f"  Throughput:      {results['throughput_seq_per_sec']:.2f} seq/sec")
    print(f"  Batch Size:      {results['batch_size']}")
    print(f"  Sequence Length: {results['sequence_length']}")
    print()


def example_backend_detection():
    """Backend detection example"""
    print("=" * 70)
    print("Example 5: Backend Detection")
    print("=" * 70)
    
    from neuratensor.sdk.backends import detect_backend, print_backend_info
    
    # Detect backend
    print("\n1. Auto-detecting backend...")
    backend = detect_backend()
    
    print(f"   Backend: {backend.name}")
    print(f"   Device: {backend.device_name}")
    print(f"   Compute Capability: {backend.compute_capability}")
    
    # Print full info
    print("\n2. Full backend information:")
    print_backend_info()
    print()


def example_model_info():
    """Model information example"""
    print("=" * 70)
    print("Example 6: Model Information")
    print("=" * 70)
    
    from neuratensor.sdk import NeuraTensor
    
    # Load model
    print("\n1. Loading model...")
    model = NeuraTensor.from_pretrained("64m")
    
    # Get info
    print("2. Getting model info...")
    info = model.get_model_info()
    
    print("\nModel Information:")
    for key, value in info.items():
        print(f"  {key:25s}: {value}")
    print()


def run_all_examples():
    """Run all examples"""
    examples = [
        example_basic_inference,
        example_custom_config,
        example_generation,
        example_benchmark,
        example_backend_detection,
        example_model_info,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            print()


if __name__ == "__main__":
    print("\n")
    print("█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + " " * 20 + "NEURATENSOR SDK EXAMPLES" + " " * 24 + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    print("\n")
    
    run_all_examples()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
