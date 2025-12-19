"""
Command-line interface for Hamerspace.
"""

import argparse
import sys
from pathlib import Path
import json

from hamerspace import Optimizer, OptimizationGoal, Constraints
from hamerspace.utils.logger import set_log_level, get_logger
import logging


logger = get_logger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Hamerspace - Model Compression and Optimization Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quantize a PyTorch model
  hamerspace optimize model.pt --goal quantize --size 10 --output optimized.pt

  # Auto optimization with constraints
  hamerspace optimize model.onnx --goal auto --size 5 --latency 50 --hardware cpu

  # Benchmark a model
  hamerspace benchmark model.pt --hardware cpu --runs 100
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize a model')
    optimize_parser.add_argument('model', type=str, help='Path to model file')
    optimize_parser.add_argument(
        '--framework',
        choices=['pytorch', 'tensorflow', 'onnx'],
        help='Model framework (auto-detected if not specified)'
    )
    optimize_parser.add_argument(
        '--goal',
        choices=['quantize', 'prune', 'distill', 'auto'],
        default='auto',
        help='Optimization goal (default: auto)'
    )
    optimize_parser.add_argument(
        '--size',
        type=float,
        help='Target model size in MB'
    )
    optimize_parser.add_argument(
        '--latency',
        type=float,
        help='Max latency in milliseconds'
    )
    optimize_parser.add_argument(
        '--accuracy-drop',
        type=float,
        help='Max accuracy drop (0.0-1.0)'
    )
    optimize_parser.add_argument(
        '--hardware',
        choices=['cpu', 'arm', 'edge', 'gpu', 'cuda'],
        default='cpu',
        help='Target hardware (default: cpu)'
    )
    optimize_parser.add_argument(
        '--input-shape',
        type=str,
        help='Input shape as comma-separated values (e.g., "1,3,224,224")'
    )
    optimize_parser.add_argument(
        '--output',
        type=str,
        help='Output path for optimized model'
    )
    optimize_parser.add_argument(
        '--report',
        type=str,
        help='Path to save optimization report'
    )
    optimize_parser.add_argument(
        '--config',
        type=str,
        help='Path to save optimization config (for reproducibility)'
    )
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser('benchmark', help='Benchmark a model')
    benchmark_parser.add_argument('model', type=str, help='Path to model file')
    benchmark_parser.add_argument(
        '--framework',
        choices=['pytorch', 'tensorflow', 'onnx'],
        help='Model framework (auto-detected if not specified)'
    )
    benchmark_parser.add_argument(
        '--hardware',
        choices=['cpu', 'arm', 'edge', 'gpu', 'cuda'],
        default='cpu',
        help='Hardware to benchmark on (default: cpu)'
    )
    benchmark_parser.add_argument(
        '--runs',
        type=int,
        default=100,
        help='Number of inference runs (default: 100)'
    )
    benchmark_parser.add_argument(
        '--batch-size',
        type=int,
        default=1,
        help='Batch size (default: 1)'
    )
    benchmark_parser.add_argument(
        '--input-shape',
        type=str,
        help='Input shape as comma-separated values (e.g., "1,3,224,224")'
    )
    
    # Global options
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='hamerspace 0.1.0'
    )
    
    return parser.parse_args()


def parse_input_shape(shape_str):
    """Parse input shape string to list of ints."""
    if not shape_str:
        return None
    try:
        return [int(x.strip()) for x in shape_str.split(',')]
    except ValueError:
        logger.error(f"Invalid input shape: {shape_str}")
        sys.exit(1)


def detect_framework(model_path):
    """Detect model framework from file extension."""
    path = Path(model_path)
    suffix = path.suffix.lower()
    
    if suffix in ['.pt', '.pth']:
        return 'pytorch'
    elif suffix in ['.h5', '.keras']:
        return 'tensorflow'
    elif suffix == '.onnx':
        return 'onnx'
    elif path.is_dir():
        # Could be TensorFlow SavedModel
        return 'tensorflow'
    else:
        logger.error(f"Cannot detect framework for: {model_path}")
        sys.exit(1)


def load_model(model_path, framework, input_shape):
    """Load model based on framework."""
    if framework == 'pytorch':
        return Optimizer.from_pytorch(model_path, input_shape)
    elif framework == 'tensorflow':
        return Optimizer.from_tensorflow(model_path, input_shape)
    elif framework == 'onnx':
        return Optimizer.from_onnx(model_path)
    else:
        logger.error(f"Unsupported framework: {framework}")
        sys.exit(1)


def optimize_command(args):
    """Handle optimize command."""
    # Parse input shape
    input_shape = parse_input_shape(args.input_shape)
    
    # Detect framework if not specified
    framework = args.framework or detect_framework(args.model)
    
    logger.info(f"Loading {framework} model from {args.model}")
    
    # Load model
    optimizer = load_model(args.model, framework, input_shape)
    
    # Create constraints
    constraints = Constraints(
        target_size_mb=args.size,
        max_latency_ms=args.latency,
        max_accuracy_drop=args.accuracy_drop,
        target_hardware=args.hardware
    )
    
    logger.info(f"Optimizing with goal: {args.goal}")
    
    # Optimize
    goal = OptimizationGoal(args.goal)
    result = optimizer.optimize(
        goal=goal,
        constraints=constraints
    )
    
    # Print report
    print("\n" + str(result.report))
    
    # Save optimized model
    if args.output:
        output_path = Path(args.output)
        result.save_model(output_path)
        logger.info(f"Saved optimized model to {output_path}")
    
    # Save report
    if args.report:
        report_path = Path(args.report)
        result.save_report(report_path)
        logger.info(f"Saved report to {report_path}")
    
    # Save config
    if args.config:
        config_path = Path(args.config)
        result.save_config(config_path)
        logger.info(f"Saved config to {config_path}")
    
    # Exit with success/failure based on constraints
    if result.report.constraints_satisfied:
        sys.exit(0)
    else:
        logger.warning("Constraints not fully satisfied")
        sys.exit(1)


def benchmark_command(args):
    """Handle benchmark command."""
    # Parse input shape
    input_shape = parse_input_shape(args.input_shape)
    
    # Detect framework if not specified
    framework = args.framework or detect_framework(args.model)
    
    logger.info(f"Loading {framework} model from {args.model}")
    
    # Load model
    optimizer = load_model(args.model, framework, input_shape)
    
    logger.info(f"Benchmarking on {args.hardware}")
    
    # Benchmark
    metrics = optimizer.benchmark(
        hardware=args.hardware,
        num_runs=args.runs,
        batch_size=args.batch_size
    )
    
    # Print results
    print("\n" + "=" * 60)
    print("Benchmark Results")
    print("=" * 60)
    print(f"Model Size: {metrics.size_mb:.2f} MB")
    print(f"Latency: {metrics.latency_ms:.2f} ms (avg over {args.runs} runs)")
    print(f"Throughput: {metrics.throughput:.2f} inferences/second")
    if metrics.memory_mb:
        print(f"Memory Usage: {metrics.memory_mb:.2f} MB")
    print("=" * 60)


def main():
    """Main entry point for CLI."""
    args = parse_args()
    
    # Set log level
    if args.verbose:
        set_log_level(logging.DEBUG)
    else:
        set_log_level(logging.INFO)
    
    # Run command
    if args.command == 'optimize':
        optimize_command(args)
    elif args.command == 'benchmark':
        benchmark_command(args)
    else:
        print("Error: No command specified. Use --help for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
