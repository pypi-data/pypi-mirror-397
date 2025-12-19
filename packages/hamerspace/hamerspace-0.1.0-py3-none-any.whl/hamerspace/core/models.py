"""
Core data models for Hamerspace using Pydantic for validation.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


class OptimizationGoal(str, Enum):
    """Available optimization goals."""
    QUANTIZE = "quantize"
    PRUNE = "prune"
    DISTILL = "distill"
    AUTO = "auto"


class Backend(str, Enum):
    """Available backend toolkits."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    ONNX_RUNTIME = "onnx_runtime"
    OPENVINO = "openvino"
    TVM = "tvm"
    OPTIMUM = "optimum"
    BITSANDBYTES = "bitsandbytes"


class TargetHardware(str, Enum):
    """Target hardware platforms."""
    CPU = "cpu"
    ARM = "arm"
    EDGE = "edge"
    GPU = "gpu"
    CUDA = "cuda"


class ModelFramework(str, Enum):
    """Supported model frameworks."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    KERAS = "keras"


class Constraints(BaseModel):
    """User-defined optimization constraints."""
    
    target_size_mb: Optional[float] = Field(
        None,
        description="Target model size in megabytes",
        gt=0
    )
    
    max_latency_ms: Optional[float] = Field(
        None,
        description="Maximum inference latency in milliseconds",
        gt=0
    )
    
    max_accuracy_drop: Optional[float] = Field(
        None,
        description="Maximum acceptable accuracy drop (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    target_hardware: TargetHardware = Field(
        TargetHardware.CPU,
        description="Target hardware platform"
    )
    
    batch_size: int = Field(
        1,
        description="Inference batch size for benchmarking",
        gt=0
    )
    
    calibration_samples: int = Field(
        100,
        description="Number of samples for calibration (quantization)",
        gt=0
    )
    
    @field_validator('max_accuracy_drop')
    @classmethod
    def validate_accuracy_drop(cls, v):
        if v is not None and v > 1.0:
            raise ValueError("max_accuracy_drop must be between 0.0 and 1.0")
        return v
    
    def has_size_constraint(self) -> bool:
        """Check if size constraint is specified."""
        return self.target_size_mb is not None
    
    def has_latency_constraint(self) -> bool:
        """Check if latency constraint is specified."""
        return self.max_latency_ms is not None
    
    def has_accuracy_constraint(self) -> bool:
        """Check if accuracy constraint is specified."""
        return self.max_accuracy_drop is not None


class ModelMetrics(BaseModel):
    """Performance metrics for a model."""
    
    size_mb: float = Field(description="Model size in megabytes")
    latency_ms: float = Field(description="Average inference latency in milliseconds")
    accuracy: Optional[float] = Field(None, description="Model accuracy (if evaluable)")
    memory_mb: Optional[float] = Field(None, description="Peak memory usage in MB")
    throughput: Optional[float] = Field(None, description="Inferences per second")
    
    def __str__(self) -> str:
        parts = [
            f"Size: {self.size_mb:.2f} MB",
            f"Latency: {self.latency_ms:.2f} ms"
        ]
        if self.accuracy is not None:
            parts.append(f"Accuracy: {self.accuracy:.4f}")
        if self.throughput is not None:
            parts.append(f"Throughput: {self.throughput:.2f} inf/s")
        return ", ".join(parts)


class OptimizationConfig(BaseModel):
    """Configuration for a specific optimization strategy."""
    
    goal: OptimizationGoal
    backend: Backend
    technique: str = Field(description="Specific technique (e.g., 'int8', 'dynamic')")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        frozen = True  # Make immutable for reproducibility


class CompressionReport(BaseModel):
    """Detailed report comparing original and optimized models."""
    
    original_metrics: ModelMetrics
    optimized_metrics: ModelMetrics
    optimization_config: OptimizationConfig
    
    size_reduction_ratio: float = Field(description="Size reduction ratio")
    latency_improvement_ratio: float = Field(description="Latency improvement ratio")
    accuracy_drop: Optional[float] = Field(None, description="Accuracy drop if measurable")
    
    constraints_satisfied: bool = Field(description="Whether all constraints are satisfied")
    constraint_violations: List[str] = Field(default_factory=list)
    
    execution_time_seconds: float = Field(description="Time taken for optimization")
    backend_used: Backend
    
    def __str__(self) -> str:
        lines = [
            "=" * 60,
            "Hamerspace Optimization Report",
            "=" * 60,
            "",
            "Original Model:",
            f"  {self.original_metrics}",
            "",
            "Optimized Model:",
            f"  {self.optimized_metrics}",
            "",
            "Improvements:",
            f"  Size Reduction: {self.size_reduction_ratio:.2%}",
            f"  Latency Improvement: {self.latency_improvement_ratio:.2%}",
        ]
        
        if self.accuracy_drop is not None:
            lines.append(f"  Accuracy Drop: {self.accuracy_drop:.4f}")
        
        lines.extend([
            "",
            f"Backend: {self.backend_used.value}",
            f"Technique: {self.optimization_config.technique}",
            f"Optimization Time: {self.execution_time_seconds:.2f}s",
            "",
            f"Constraints Satisfied: {'✓ Yes' if self.constraints_satisfied else '✗ No'}",
        ])
        
        if self.constraint_violations:
            lines.append("\nConstraint Violations:")
            for violation in self.constraint_violations:
                lines.append(f"  • {violation}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class ModelInfo(BaseModel):
    """Information about a loaded model."""
    
    framework: ModelFramework
    input_shape: Optional[List[int]] = None
    output_shape: Optional[List[int]] = None
    num_parameters: Optional[int] = None
    model_type: Optional[str] = None  # e.g., "resnet50", "efficientnet"
    has_batch_norm: bool = False
    has_dropout: bool = False
    
    def __str__(self) -> str:
        parts = [f"Framework: {self.framework.value}"]
        if self.num_parameters:
            parts.append(f"Parameters: {self.num_parameters:,}")
        if self.model_type:
            parts.append(f"Type: {self.model_type}")
        return ", ".join(parts)
