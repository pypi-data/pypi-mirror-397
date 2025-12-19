# Hamerspace 🔨

**A compiler-style optimization pass for non-LLM machine learning models**

Hamerspace is a model compression and optimization engine that orchestrates existing open-source toolkits to compress and optimize computer vision, audio, time-series, and tabular ML models.

## Features

- 🎯 **Goal-oriented optimization**: Specify what you want (size, latency, accuracy) and let Hamerspace figure out how
- 🔧 **Multi-backend orchestration**: Automatically selects and composes tools from PyTorch, TensorFlow, ONNX, OpenVINO, TVM, and more
- 📊 **Comprehensive benchmarking**: Measures size, latency, and accuracy before and after optimization
- 🎨 **Hardware-aware**: Optimizes for specific target hardware (CPU, ARM, edge devices)
- 📦 **Deployment-ready**: Produces optimized model artifacts ready for production

## Installation

```bash
pip install hamerspace
```

For full backend support (OpenVINO, TVM, bitsandbytes):

```bash
pip install hamerspace[full]
```

## Quick Start

```python
from hamerspace import Optimizer, OptimizationGoal, Constraints

# Load your trained model
optimizer = Optimizer.from_pytorch("model.pt")

# Define constraints
constraints = Constraints(
    target_size_mb=10,          # Must be under 10MB
    max_latency_ms=50,          # Must inference in <50ms
    max_accuracy_drop=0.02,     # Max 2% accuracy drop
    target_hardware="cpu"       # Optimize for CPU
)

# Optimize
result = optimizer.optimize(
    goal=OptimizationGoal.AUTO,
    constraints=constraints
)

# Save optimized model
result.save_model("optimized_model.onnx")

# View report
print(result.report)
```

## Optimization Goals

- **`OptimizationGoal.QUANTIZE`**: Apply quantization (INT8, INT4)
- **`OptimizationGoal.PRUNE`**: Remove unnecessary weights
- **`OptimizationGoal.DISTILL`**: Knowledge distillation (requires training data)
- **`OptimizationGoal.AUTO`**: Automatically select best techniques

## Supported Frameworks

### Input Models
- PyTorch (.pt, .pth)
- TensorFlow (.h5, SavedModel)
- ONNX (.onnx)

### Backend Toolkits
- PyTorch (quantization, pruning)
- TensorFlow (quantization)
- ONNX Runtime (quantization, graph optimization)
- OpenVINO (optimization for Intel hardware)
- Apache TVM (compilation and optimization)
- Hugging Face Optimum (hardware-specific optimization)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Public API Layer                    │
│         (Optimizer, Constraints, Goals)              │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Orchestration Layer                     │
│    (Strategy Selection, Pipeline Composition)        │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│               Backend Layer                          │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │ PyTorch  │   ONNX   │ OpenVINO │   TVM    │     │
│  │ Backend  │ Backend  │ Backend  │ Backend  │     │
│  └──────────┴──────────┴──────────┴──────────┘     │
└─────────────────────────────────────────────────────┘
```

## Advanced Usage

### Custom Backend Selection

```python
from hamerspace import Optimizer, Backend

optimizer = Optimizer.from_pytorch("model.pt")
result = optimizer.optimize(
    goal=OptimizationGoal.QUANTIZE,
    constraints=constraints,
    preferred_backends=[Backend.ONNX, Backend.OPENVINO]
)
```

### Benchmarking Only

```python
# Benchmark without optimization
metrics = optimizer.benchmark(
    hardware="cpu",
    num_runs=100
)
print(f"Latency: {metrics.latency_ms}ms")
print(f"Size: {metrics.size_mb}MB")
```

### Export Optimization Config

```python
# Save configuration for reproducibility
result.save_config("optimization_config.json")

# Reproduce optimization
from hamerspace import Optimizer
optimizer = Optimizer.from_config("optimization_config.json")
result = optimizer.apply()
```

## Non-Goals

❌ LLM optimization (use specialized tools like vLLM, TensorRT-LLM)  
❌ Training models from scratch  
❌ Research or SOTA benchmarking  
❌ Custom kernel development  

## Requirements

- Python 3.8+
- One or more supported backends installed

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## License

Apache License 2.0

## Citation

```bibtex
@software{hamerspace2025,
  title={Hamerspace: Model Compression and Optimization Engine},
  author={Hamerspace Contributors},
  year={2025},
  url={https://github.com/yourusername/hamerspace}
}
```
