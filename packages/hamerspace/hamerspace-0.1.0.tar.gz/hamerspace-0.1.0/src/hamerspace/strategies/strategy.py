"""
Optimization strategies that compose backend operations.
"""

from typing import Any, Optional, List
from abc import ABC, abstractmethod

from hamerspace.core.models import (
    OptimizationConfig,
    Constraints,
    OptimizationGoal,
    Backend,
)
from hamerspace.backends.base import BaseBackend
from hamerspace.utils.logger import get_logger

logger = get_logger(__name__)


class OptimizationStrategy(ABC):
    """
    Base class for optimization strategies.
    
    A strategy encapsulates a specific optimization technique
    (e.g., INT8 quantization via ONNX) and knows how to apply it.
    """
    
    def __init__(
        self,
        config: OptimizationConfig,
        backend: BaseBackend,
    ):
        self.config = config
        self.backend = backend
    
    @abstractmethod
    def apply(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
        validation_data: Optional[Any] = None,
    ) -> Any:
        """
        Apply this optimization strategy to the model.
        
        Args:
            model: Model to optimize
            input_shape: Input tensor shape
            constraints: Optimization constraints
            validation_data: Data for validation/calibration
        
        Returns:
            Optimized model
        """
        pass
    
    @abstractmethod
    def estimate_impact(
        self,
        model_size_mb: float,
        latency_ms: float,
    ) -> tuple[float, float]:
        """
        Estimate the impact of this strategy.
        
        Args:
            model_size_mb: Original model size
            latency_ms: Original latency
        
        Returns:
            (estimated_new_size_mb, estimated_new_latency_ms)
        """
        pass


class QuantizationStrategy(OptimizationStrategy):
    """Strategy for quantization-based optimization."""
    
    def apply(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
        validation_data: Optional[Any] = None,
    ) -> Any:
        logger.info(f"Applying quantization via {self.backend.name}")
        
        return self.backend.quantize(
            model=model,
            input_shape=input_shape,
            constraints=constraints,
            calibration_data=validation_data,
        )
    
    def estimate_impact(
        self,
        model_size_mb: float,
        latency_ms: float,
    ) -> tuple[float, float]:
        # INT8 quantization typically gives ~4x size reduction
        # and 1.5-2x latency improvement
        if "int8" in self.config.technique.lower():
            return model_size_mb * 0.25, latency_ms * 0.6
        elif "int4" in self.config.technique.lower():
            return model_size_mb * 0.125, latency_ms * 0.5
        else:
            # Dynamic quantization - less aggressive
            return model_size_mb * 0.5, latency_ms * 0.8


class PruningStrategy(OptimizationStrategy):
    """Strategy for pruning-based optimization."""
    
    def apply(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
        validation_data: Optional[Any] = None,
    ) -> Any:
        logger.info(f"Applying pruning via {self.backend.name}")
        
        return self.backend.prune(
            model=model,
            input_shape=input_shape,
            constraints=constraints,
        )
    
    def estimate_impact(
        self,
        model_size_mb: float,
        latency_ms: float,
    ) -> tuple[float, float]:
        # Pruning typically gives 2-3x size reduction
        # with moderate latency improvement
        return model_size_mb * 0.4, latency_ms * 0.7


class GraphOptimizationStrategy(OptimizationStrategy):
    """Strategy for graph-level optimizations (fusion, etc.)."""
    
    def apply(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
        validation_data: Optional[Any] = None,
    ) -> Any:
        logger.info(f"Applying graph optimization via {self.backend.name}")
        
        return self.backend.optimize_graph(
            model=model,
            input_shape=input_shape,
            constraints=constraints,
        )
    
    def estimate_impact(
        self,
        model_size_mb: float,
        latency_ms: float,
    ) -> tuple[float, float]:
        # Graph optimization mainly improves latency
        # with minimal size impact
        return model_size_mb * 0.95, latency_ms * 0.8


class CompositeStrategy(OptimizationStrategy):
    """
    Strategy that composes multiple optimization techniques.
    
    For example: quantization + graph optimization
    """
    
    def __init__(
        self,
        config: OptimizationConfig,
        strategies: List[OptimizationStrategy],
    ):
        # Use the backend from the first strategy
        super().__init__(config, strategies[0].backend if strategies else None)
        self.strategies = strategies
    
    def apply(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
        validation_data: Optional[Any] = None,
    ) -> Any:
        logger.info(f"Applying composite strategy with {len(self.strategies)} steps")
        
        optimized_model = model
        for i, strategy in enumerate(self.strategies):
            logger.info(f"Step {i+1}/{len(self.strategies)}: {strategy.config.technique}")
            optimized_model = strategy.apply(
                optimized_model,
                input_shape,
                constraints,
                validation_data,
            )
        
        return optimized_model
    
    def estimate_impact(
        self,
        model_size_mb: float,
        latency_ms: float,
    ) -> tuple[float, float]:
        # Apply each strategy's impact sequentially
        current_size = model_size_mb
        current_latency = latency_ms
        
        for strategy in self.strategies:
            current_size, current_latency = strategy.estimate_impact(
                current_size,
                current_latency,
            )
        
        return current_size, current_latency
