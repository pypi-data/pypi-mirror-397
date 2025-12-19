"""
Base backend interface that all optimization backends must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List
from pathlib import Path

from hamerspace.core.models import (
    OptimizationConfig,
    Constraints,
    ModelInfo,
)


class BaseBackend(ABC):
    """
    Abstract base class for optimization backends.
    
    Each backend (PyTorch, ONNX, OpenVINO, etc.) must implement
    these methods to provide a consistent interface to the orchestrator.
    """
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this backend is available in the current environment.
        
        Returns:
            True if backend dependencies are installed
        """
        pass
    
    @abstractmethod
    def supports_model(self, model_info: ModelInfo) -> bool:
        """
        Check if this backend can handle the given model.
        
        Args:
            model_info: Information about the model
        
        Returns:
            True if backend can optimize this model
        """
        pass
    
    @abstractmethod
    def can_satisfy_constraints(
        self,
        constraints: Constraints,
        model_info: ModelInfo,
    ) -> bool:
        """
        Check if this backend can potentially satisfy the constraints.
        
        Args:
            constraints: User-defined constraints
            model_info: Information about the model
        
        Returns:
            True if backend might satisfy constraints
        """
        pass
    
    @abstractmethod
    def quantize(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
        calibration_data: Optional[Any] = None,
    ) -> Any:
        """
        Apply quantization to the model.
        
        Args:
            model: Model to quantize
            input_shape: Input tensor shape
            constraints: Optimization constraints
            calibration_data: Data for calibration-based quantization
        
        Returns:
            Quantized model
        """
        pass
    
    @abstractmethod
    def prune(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
    ) -> Any:
        """
        Apply pruning to the model.
        
        Args:
            model: Model to prune
            input_shape: Input tensor shape
            constraints: Optimization constraints
        
        Returns:
            Pruned model
        """
        pass
    
    @abstractmethod
    def optimize_graph(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
    ) -> Any:
        """
        Apply graph-level optimizations.
        
        Args:
            model: Model to optimize
            input_shape: Input tensor shape
            constraints: Optimization constraints
        
        Returns:
            Optimized model
        """
        pass
    
    @abstractmethod
    def save_model(self, model: Any, path: Path) -> None:
        """
        Save the optimized model to disk.
        
        Args:
            model: Model to save
            path: Output path
        """
        pass
    
    @abstractmethod
    def load_model(self, path: Path) -> Any:
        """
        Load a model from disk.
        
        Args:
            path: Path to model file
        
        Returns:
            Loaded model
        """
        pass
    
    def get_capabilities(self) -> List[str]:
        """
        Get list of optimization techniques this backend supports.
        
        Returns:
            List of capability strings
        """
        capabilities = []
        
        # Check if methods are implemented (not just pass)
        try:
            # This is a simple heuristic - override in subclasses for accuracy
            if hasattr(self, 'quantize'):
                capabilities.append('quantize')
            if hasattr(self, 'prune'):
                capabilities.append('prune')
            if hasattr(self, 'optimize_graph'):
                capabilities.append('graph_optimization')
        except:
            pass
        
        return capabilities
    
    def __str__(self) -> str:
        return f"{self.name}Backend"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
