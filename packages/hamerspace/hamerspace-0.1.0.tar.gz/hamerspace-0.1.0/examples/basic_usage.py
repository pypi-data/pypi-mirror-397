"""
Example usage of Hamerspace for model optimization.
"""

import torch
import torch.nn as nn
from hamerspace import Optimizer, OptimizationGoal, Constraints


# Example 1: Simple quantization of a PyTorch model
def example_basic_quantization():
    """Basic quantization example."""
    print("=" * 60)
    print("Example 1: Basic Quantization")
    print("=" * 60)
    
    # Create a simple model
    class SimpleNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
            self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
            self.fc = nn.Linear(128 * 8 * 8, 10)
            self.relu = nn.ReLU()
            self.pool = nn.MaxPool2d(2)
        
        def forward(self, x):
            x = self.relu(self.conv1(x))
            x = self.pool(x)
            x = self.relu(self.conv2(x))
            x = self.pool(x)
            x = x.view(x.size(0), -1)
            x = self.fc(x)
            return x
    
    model = SimpleNet()
    model.eval()
    
    # Initialize optimizer
    optimizer = Optimizer.from_pytorch(
        model,
        input_shape=[1, 3, 32, 32]
    )
    
    # Define constraints
    constraints = Constraints(
        target_size_mb=5,
        max_latency_ms=10,
        target_hardware="cpu"
    )
    
    # Optimize
    result = optimizer.optimize(
        goal=OptimizationGoal.QUANTIZE,
        constraints=constraints
    )
    
    # Print report
    print(result.report)
    
    # Save optimized model
    result.save_model("optimized_simple_net.pt")
    print("\nOptimized model saved to optimized_simple_net.pt")


# Example 2: Auto optimization with accuracy validation
def example_auto_optimization_with_validation():
    """Auto optimization with accuracy checking."""
    print("\n" + "=" * 60)
    print("Example 2: Auto Optimization with Validation")
    print("=" * 60)
    
    # Create a model
    model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=False)
    model.eval()
    
    # Initialize optimizer
    optimizer = Optimizer.from_pytorch(
        model,
        input_shape=[1, 3, 224, 224]
    )
    
    # Define validation function
    def validate(model):
        """Dummy validation function."""
        # In practice, this would run the model on a validation set
        # and return accuracy
        return 0.75  # Placeholder
    
    # Define constraints
    constraints = Constraints(
        target_size_mb=20,
        max_latency_ms=50,
        max_accuracy_drop=0.05,  # Max 5% accuracy drop
        target_hardware="cpu"
    )
    
    # Optimize with AUTO goal
    result = optimizer.optimize(
        goal=OptimizationGoal.AUTO,
        constraints=constraints,
        validation_fn=validate
    )
    
    print(result.report)
    
    # Save everything
    result.save_model("optimized_resnet18.pt")
    result.save_config("optimization_config.json")
    result.save_report("optimization_report.txt")


# Example 3: Benchmarking only
def example_benchmarking():
    """Just benchmark a model without optimization."""
    print("\n" + "=" * 60)
    print("Example 3: Benchmarking Only")
    print("=" * 60)
    
    # Create a model
    class TinyNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = nn.Linear(784, 128)
            self.fc2 = nn.Linear(128, 10)
            self.relu = nn.ReLU()
        
        def forward(self, x):
            x = x.view(x.size(0), -1)
            x = self.relu(self.fc1(x))
            x = self.fc2(x)
            return x
    
    model = TinyNet()
    model.eval()
    
    # Initialize optimizer
    optimizer = Optimizer.from_pytorch(
        model,
        input_shape=[1, 1, 28, 28]
    )
    
    # Benchmark
    metrics = optimizer.benchmark(
        hardware="cpu",
        num_runs=100,
        batch_size=1
    )
    
    print(f"\nBenchmark Results:")
    print(f"  Size: {metrics.size_mb:.2f} MB")
    print(f"  Latency: {metrics.latency_ms:.2f} ms")
    print(f"  Throughput: {metrics.throughput:.2f} inferences/sec")


# Example 4: Advanced - composite optimization
def example_composite_optimization():
    """Advanced example with multiple optimization techniques."""
    print("\n" + "=" * 60)
    print("Example 4: Composite Optimization")
    print("=" * 60)
    
    # Create a larger model
    model = torch.hub.load('pytorch/vision:v0.10.0', 'mobilenet_v2', pretrained=False)
    model.eval()
    
    # Initialize optimizer
    optimizer = Optimizer.from_pytorch(
        model,
        input_shape=[1, 3, 224, 224]
    )
    
    # Aggressive constraints that require multiple techniques
    constraints = Constraints(
        target_size_mb=3,  # Very small
        max_latency_ms=30,  # Very fast
        max_accuracy_drop=0.03,
        target_hardware="cpu"
    )
    
    # Use AUTO to let Hamerspace compose techniques
    result = optimizer.optimize(
        goal=OptimizationGoal.AUTO,
        constraints=constraints
    )
    
    print(result.report)
    print(f"\nOptimization technique used: {result.config.technique}")
    print(f"Backend: {result.config.backend.value}")


# Example 5: Hardware-specific optimization
def example_hardware_specific():
    """Optimize for specific hardware."""
    print("\n" + "=" * 60)
    print("Example 5: Hardware-Specific Optimization")
    print("=" * 60)
    
    model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=False)
    model.eval()
    
    optimizer = Optimizer.from_pytorch(
        model,
        input_shape=[1, 3, 224, 224]
    )
    
    # Optimize for edge device
    constraints = Constraints(
        target_size_mb=10,
        max_latency_ms=100,
        target_hardware="edge"  # Will prefer OpenVINO if available
    )
    
    result = optimizer.optimize(
        goal=OptimizationGoal.QUANTIZE,
        constraints=constraints
    )
    
    print(result.report)


if __name__ == "__main__":
    # Run examples
    try:
        example_basic_quantization()
    except Exception as e:
        print(f"Example 1 failed: {e}")
    
    try:
        example_benchmarking()
    except Exception as e:
        print(f"Example 3 failed: {e}")
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nNote: Some examples may fail if required backends are not installed.")
    print("Install with: pip install hamerspace[full]")
