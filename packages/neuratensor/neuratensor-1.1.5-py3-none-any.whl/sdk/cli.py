"""
NeuraTensor CLI - Command Line Interface
=========================================

CLI tool for model management and inference.
"""

import argparse
import sys
from pathlib import Path

from . import __version__, NeuraTensor
from .model_loader import ModelLoader
from .config import NeuraTensorConfig


def cmd_info(args):
    """Display system and model information"""
    print(f"NeuraTensor SDK v{__version__}")
    print("-" * 50)
    
    # Import here to avoid loading CUDA if not needed
    import torch
    
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"Device Name: {torch.cuda.get_device_name(0)}")
        print(f"Device Count: {torch.cuda.device_count()}")


def cmd_run(args):
    """Run inference with a model"""
    print(f"Loading model: {args.model}")
    
    # Load model
    loader = ModelLoader()
    model = loader.load(args.model, device=args.device)
    
    # Create inference engine
    engine = InferenceEngine(model)
    
    # Prepare input
    import torch
    if args.input:
        # Load input from file
        input_data = torch.load(args.input)
    else:
        # Generate random input for testing
        config = model.config
        input_data = torch.randint(
            0, config.vocab_size,
            (1, args.seq_length),
            device=args.device
        )
    
    print(f"Running inference...")
    result = engine.infer(input_data, return_logits=True)
    
    print(f"\nResults:")
    print(f"  Latency: {result['latency_ms']:.2f}ms")
    print(f"  Output shape: {result['logits'].shape}")
    
    if args.output:
        torch.save(result, args.output)
        print(f"  Saved to: {args.output}")


def cmd_benchmark(args):
    """Benchmark model performance"""
    import torch
    import statistics
    
    # Header
    print("\n" + "=" * 60)
    print(f"NeuraTensor {args.model.upper()} | Benchmark")
    print("=" * 60)
    
    # Device info
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        compute_cap = torch.cuda.get_device_capability(0)
        print(f"Device:    {device_name} (SM {compute_cap[0]}.{compute_cap[1]})")
        print(f"CUDA:      {torch.version.cuda}")
    else:
        print("Device:    CPU")
    
    print("-" * 60)
    
    # Load model using public API
    from . import NeuraTensor, NeuraTensorConfig
    
    print(f"Loading {args.model} configuration...")
    config = NeuraTensorConfig.preset(args.model)
    model = NeuraTensor(config)
    
    if args.device == "cuda" and torch.cuda.is_available():
        model = model.cuda().half()
        print(f"✓ Model loaded on CUDA")
    else:
        print(f"✓ Model loaded on CPU")
    
    print(f"✓ Parameters: {model.count_parameters():,}")
    print("-" * 60)
    
    # Prepare input
    device = "cuda" if args.device == "cuda" and torch.cuda.is_available() else "cpu"
    input_ids = torch.randint(
        0,
        config.vocab_size,
        (args.batch_size, args.seq_length),
        device=device
    )
    
    # Warmup
    print(f"Warming up ({args.warmup} iterations)...")
    with torch.no_grad():
        for _ in range(args.warmup):
            _ = model(input_ids)
            if device == "cuda":
                torch.cuda.synchronize()
    print("✓ Warmup complete")
    
    # Benchmark
    print(f"Benchmarking ({args.iterations} iterations)...")
    latencies = []
    
    with torch.no_grad():
        for i in range(args.iterations):
            if device == "cuda":
                torch.cuda.synchronize()
                start = torch.cuda.Event(enable_timing=True)
                end = torch.cuda.Event(enable_timing=True)
                
                start.record()
                output = model(input_ids)
                end.record()
                
                torch.cuda.synchronize()
                latency_ms = start.elapsed_time(end)
            else:
                import time
                start = time.perf_counter()
                output = model(input_ids)
                end = time.perf_counter()
                latency_ms = (end - start) * 1000
            
            latencies.append(latency_ms)
            
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{args.iterations}")
    
    # Calculate statistics
    mean_lat = statistics.mean(latencies)
    std_lat = statistics.stdev(latencies) if len(latencies) > 1 else 0
    min_lat = min(latencies)
    max_lat = max(latencies)
    p99_lat = sorted(latencies)[int(len(latencies) * 0.99)]
    throughput = 1000 / mean_lat * args.batch_size
    
    # Results
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Latency (mean):    {mean_lat:.2f} ms ± {std_lat:.2f} ms")
    print(f"Latency (p99):     {p99_lat:.2f} ms")
    print(f"Latency (min):     {min_lat:.2f} ms")
    print(f"Latency (max):     {max_lat:.2f} ms")
    print(f"Throughput:        {throughput:.1f} seq/s")
    print(f"Batch size:        {args.batch_size}")
    print(f"Sequence length:   {args.seq_length}")
    print(f"Kernel:            fused_snn_ssm (secure)")
    print("=" * 60)
    print("✓ Benchmark complete")
    print()


def cmd_list(args):
    """List available models"""
    loader = ModelLoader()
    models = loader.list_available_models()
    
    print("Available Models:")
    print("-" * 50)
    for model_name in models:
        print(f"  - {model_name}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="neuratensor",
        description="NeuraTensor SDK - Neuromorphic Tensor Processing"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Info command
    parser_info = subparsers.add_parser("info", help="Display system information")
    parser_info.set_defaults(func=cmd_info)
    
    # Run command
    parser_run = subparsers.add_parser("run", help="Run inference")
    parser_run.add_argument("model", help="Model name or path")
    parser_run.add_argument("--input", help="Input file path")
    parser_run.add_argument("--output", help="Output file path")
    parser_run.add_argument("--device", default="cuda", help="Device (cuda/cpu)")
    parser_run.add_argument("--seq-length", type=int, default=64, help="Sequence length")
    parser_run.set_defaults(func=cmd_run)
    
    # Benchmark command
    parser_bench = subparsers.add_parser("benchmark", help="Benchmark model")
    parser_bench.add_argument("model", help="Model name or path")
    parser_bench.add_argument("--device", default="cuda", help="Device (cuda/cpu)")
    parser_bench.add_argument("--batch-size", type=int, default=1, help="Batch size")
    parser_bench.add_argument("--seq-length", type=int, default=64, help="Sequence length")
    parser_bench.add_argument("--iterations", type=int, default=30, help="Number of iterations")
    parser_bench.add_argument("--warmup", type=int, default=5, help="Warmup iterations")
    parser_bench.set_defaults(func=cmd_benchmark)
    
    # List command
    parser_list = subparsers.add_parser("list", help="List available models")
    parser_list.set_defaults(func=cmd_list)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args) or 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
