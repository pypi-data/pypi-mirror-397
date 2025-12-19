"""
Main Optimizer class - the public API entry point for Hamerspace.
"""

import time
from pathlib import Path
from typing import Optional, Union, List, Callable, Any
import json

from hamerspace.core.models import (
    OptimizationGoal,
    Backend,
    Constraints,
    ModelInfo,
    OptimizationConfig,
    ModelMetrics,
    CompressionReport,
    ModelFramework,
)
from hamerspace.strategies.strategy_selector import StrategySelector
from hamerspace.backends.base import BaseBackend
from hamerspace.backends.loader import ModelLoader
from hamerspace.benchmarks.benchmarker import Benchmarker
from hamerspace.utils.logger import get_logger


logger = get_logger(__name__)


class OptimizationResult:
    """Result of an optimization operation."""
    
    def __init__(
        self,
        optimized_model: Any,
        report: CompressionReport,
        config: OptimizationConfig,
        backend: BaseBackend,
    ):
        self.optimized_model = optimized_model
        self.report = report
        self.config = config
        self._backend = backend
    
    def save_model(self, path: Union[str, Path]) -> None:
        """Save the optimized model to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving optimized model to {path}")
        self._backend.save_model(self.optimized_model, path)
        logger.info("Model saved successfully")
    
    def save_config(self, path: Union[str, Path]) -> None:
        """Save the optimization configuration for reproducibility."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = {
            "goal": self.config.goal.value,
            "backend": self.config.backend.value,
            "technique": self.config.technique,
            "parameters": self.config.parameters,
        }
        
        with open(path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Configuration saved to {path}")
    
    def save_report(self, path: Union[str, Path]) -> None:
        """Save the optimization report."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            f.write(str(self.report))
        
        logger.info(f"Report saved to {path}")


class Optimizer:
    """
    Main optimizer class for model compression and optimization.
    
    This is the primary entry point for Hamerspace. Load a model,
    specify constraints, and let Hamerspace orchestrate the optimization.
    """
    
    def __init__(
        self,
        model: Any,
        model_info: ModelInfo,
        input_shape: Optional[List[int]] = None,
    ):
        """
        Initialize optimizer with a loaded model.
        
        Args:
            model: The loaded model object
            model_info: Information about the model
            input_shape: Input shape for the model (if not in model_info)
        """
        self.model = model
        self.model_info = model_info
        self.input_shape = input_shape or model_info.input_shape
        
        if self.input_shape is None:
            logger.warning(
                "No input shape provided. Some optimizations may require manual specification."
            )
        
        logger.info(f"Initialized optimizer with {model_info}")
    
    @classmethod
    def from_pytorch(
        cls,
        model_path: Union[str, Path, Any],
        input_shape: Optional[List[int]] = None,
    ) -> "Optimizer":
        """
        Load a PyTorch model.
        
        Args:
            model_path: Path to .pt/.pth file or PyTorch model object
            input_shape: Input tensor shape [batch, channels, height, width]
        
        Returns:
            Optimizer instance
        """
        logger.info("Loading PyTorch model")
        loader = ModelLoader()
        model, model_info = loader.load_pytorch(model_path, input_shape)
        return cls(model, model_info, input_shape)
    
    @classmethod
    def from_tensorflow(
        cls,
        model_path: Union[str, Path],
        input_shape: Optional[List[int]] = None,
    ) -> "Optimizer":
        """
        Load a TensorFlow model.
        
        Args:
            model_path: Path to .h5 file or SavedModel directory
            input_shape: Input tensor shape
        
        Returns:
            Optimizer instance
        """
        logger.info("Loading TensorFlow model")
        loader = ModelLoader()
        model, model_info = loader.load_tensorflow(model_path, input_shape)
        return cls(model, model_info, input_shape)
    
    @classmethod
    def from_onnx(
        cls,
        model_path: Union[str, Path],
    ) -> "Optimizer":
        """
        Load an ONNX model.
        
        Args:
            model_path: Path to .onnx file
        
        Returns:
            Optimizer instance
        """
        logger.info("Loading ONNX model")
        loader = ModelLoader()
        model, model_info = loader.load_onnx(model_path)
        return cls(model, model_info)
    
    @classmethod
    def from_config(cls, config_path: Union[str, Path]) -> "OptimizationResult":
        """
        Reproduce an optimization from a saved configuration.
        
        Args:
            config_path: Path to saved configuration JSON
        
        Returns:
            OptimizationResult with reproduced optimization
        """
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        
        # This would need the original model path in the config
        # Simplified for demonstration
        raise NotImplementedError(
            "Reproduction from config requires storing model path in config"
        )
    
    def optimize(
        self,
        goal: OptimizationGoal = OptimizationGoal.AUTO,
        constraints: Optional[Constraints] = None,
        validation_data: Optional[Any] = None,
        validation_fn: Optional[Callable] = None,
        preferred_backends: Optional[List[Backend]] = None,
    ) -> OptimizationResult:
        """
        Optimize the model according to the specified goal and constraints.
        
        Args:
            goal: Optimization goal (quantize, prune, distill, auto)
            constraints: User-defined constraints
            validation_data: Data for accuracy validation
            validation_fn: Custom validation function(model) -> accuracy
            preferred_backends: Preferred backends in order of preference
        
        Returns:
            OptimizationResult containing optimized model and report
        """
        start_time = time.time()
        
        # Use default constraints if none provided
        if constraints is None:
            constraints = Constraints()
        
        logger.info(f"Starting optimization with goal: {goal.value}")
        logger.info(f"Constraints: {constraints}")
        
        # Benchmark original model
        benchmarker = Benchmarker()
        original_metrics = benchmarker.benchmark_model(
            self.model,
            self.model_info,
            constraints.target_hardware,
            self.input_shape,
            batch_size=constraints.batch_size,
        )
        
        logger.info(f"Original model metrics: {original_metrics}")
        
        # Calculate original accuracy if validation provided
        original_accuracy = None
        if validation_fn is not None:
            logger.info("Evaluating original model accuracy")
            original_accuracy = validation_fn(self.model)
            original_metrics.accuracy = original_accuracy
            logger.info(f"Original accuracy: {original_accuracy:.4f}")
        
        # Select optimization strategy
        selector = StrategySelector()
        strategy = selector.select_strategy(
            goal=goal,
            constraints=constraints,
            model_info=self.model_info,
            original_metrics=original_metrics,
            preferred_backends=preferred_backends,
        )
        
        logger.info(f"Selected strategy: {strategy.config.technique} using {strategy.config.backend.value}")
        
        # Apply optimization
        optimized_model = strategy.apply(
            self.model,
            self.input_shape,
            constraints,
            validation_data,
        )
        
        # Benchmark optimized model
        optimized_metrics = benchmarker.benchmark_model(
            optimized_model,
            self.model_info,
            constraints.target_hardware,
            self.input_shape,
            batch_size=constraints.batch_size,
        )
        
        logger.info(f"Optimized model metrics: {optimized_metrics}")
        
        # Calculate optimized accuracy if validation provided
        if validation_fn is not None:
            logger.info("Evaluating optimized model accuracy")
            optimized_accuracy = validation_fn(optimized_model)
            optimized_metrics.accuracy = optimized_accuracy
            logger.info(f"Optimized accuracy: {optimized_accuracy:.4f}")
        
        # Check constraints
        constraint_violations = []
        constraints_satisfied = True
        
        if constraints.has_size_constraint():
            if optimized_metrics.size_mb > constraints.target_size_mb:
                violation = f"Size {optimized_metrics.size_mb:.2f}MB exceeds target {constraints.target_size_mb}MB"
                constraint_violations.append(violation)
                constraints_satisfied = False
        
        if constraints.has_latency_constraint():
            if optimized_metrics.latency_ms > constraints.max_latency_ms:
                violation = f"Latency {optimized_metrics.latency_ms:.2f}ms exceeds max {constraints.max_latency_ms}ms"
                constraint_violations.append(violation)
                constraints_satisfied = False
        
        if constraints.has_accuracy_constraint() and original_accuracy is not None:
            accuracy_drop = original_accuracy - optimized_metrics.accuracy
            if accuracy_drop > constraints.max_accuracy_drop:
                violation = f"Accuracy drop {accuracy_drop:.4f} exceeds max {constraints.max_accuracy_drop:.4f}"
                constraint_violations.append(violation)
                constraints_satisfied = False
        
        # Calculate improvements
        size_reduction = 1 - (optimized_metrics.size_mb / original_metrics.size_mb)
        latency_improvement = 1 - (optimized_metrics.latency_ms / original_metrics.latency_ms)
        
        accuracy_drop = None
        if original_accuracy is not None and optimized_metrics.accuracy is not None:
            accuracy_drop = original_accuracy - optimized_metrics.accuracy
        
        execution_time = time.time() - start_time
        
        # Create report
        report = CompressionReport(
            original_metrics=original_metrics,
            optimized_metrics=optimized_metrics,
            optimization_config=strategy.config,
            size_reduction_ratio=size_reduction,
            latency_improvement_ratio=latency_improvement,
            accuracy_drop=accuracy_drop,
            constraints_satisfied=constraints_satisfied,
            constraint_violations=constraint_violations,
            execution_time_seconds=execution_time,
            backend_used=strategy.config.backend,
        )
        
        logger.info(f"\n{report}")
        
        return OptimizationResult(
            optimized_model=optimized_model,
            report=report,
            config=strategy.config,
            backend=strategy.backend,
        )
    
    def benchmark(
        self,
        hardware: str = "cpu",
        num_runs: int = 100,
        batch_size: int = 1,
    ) -> ModelMetrics:
        """
        Benchmark the model without optimization.
        
        Args:
            hardware: Target hardware (cpu, gpu, etc.)
            num_runs: Number of inference runs for averaging
            batch_size: Batch size for inference
        
        Returns:
            ModelMetrics with benchmarking results
        """
        logger.info(f"Benchmarking model on {hardware}")
        
        benchmarker = Benchmarker()
        metrics = benchmarker.benchmark_model(
            self.model,
            self.model_info,
            hardware,
            self.input_shape,
            batch_size=batch_size,
            num_runs=num_runs,
        )
        
        logger.info(f"Benchmark results: {metrics}")
        return metrics
