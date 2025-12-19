"""
PyTorch backend for model optimization.
"""

from typing import Any, Optional, List
from pathlib import Path
import warnings

from hamerspace.backends.base import BaseBackend
from hamerspace.core.models import (
    Constraints,
    ModelInfo,
    ModelFramework,
    TargetHardware,
)
from hamerspace.utils.logger import get_logger

logger = get_logger(__name__)


class PyTorchBackend(BaseBackend):
    """Backend using PyTorch's native quantization and optimization tools."""
    
    def __init__(self):
        super().__init__("PyTorch")
        self._torch_available = False
        self._quantization_available = False
        
        try:
            import torch
            import torch.quantization
            self._torch_available = True
            self._quantization_available = True
        except ImportError:
            warnings.warn("PyTorch not available")
    
    def is_available(self) -> bool:
        return self._torch_available
    
    def supports_model(self, model_info: ModelInfo) -> bool:
        return model_info.framework == ModelFramework.PYTORCH
    
    def can_satisfy_constraints(
        self,
        constraints: Constraints,
        model_info: ModelInfo,
    ) -> bool:
        # PyTorch quantization works well for CPU and general optimization
        if constraints.target_hardware in [TargetHardware.CPU, TargetHardware.ARM]:
            return True
        return False
    
    def quantize(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
        calibration_data: Optional[Any] = None,
    ) -> Any:
        """
        Apply PyTorch quantization (dynamic or static).
        """
        import torch
        from torch.quantization import quantize_dynamic, prepare, convert
        
        logger.info("Applying PyTorch quantization")
        
        # Set model to eval mode
        model.eval()
        
        # Choose quantization strategy based on constraints
        if calibration_data is not None:
            # Static quantization with calibration
            logger.info("Using static quantization with calibration")
            model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
            model_prepared = prepare(model)
            
            # Calibrate with provided data
            with torch.no_grad():
                for batch in calibration_data:
                    if isinstance(batch, (list, tuple)):
                        batch = batch[0]  # Assume first element is input
                    model_prepared(batch)
            
            quantized_model = convert(model_prepared)
        else:
            # Dynamic quantization (no calibration needed)
            logger.info("Using dynamic quantization")
            quantized_model = quantize_dynamic(
                model,
                {torch.nn.Linear, torch.nn.Conv2d},
                dtype=torch.qint8
            )
        
        logger.info("PyTorch quantization complete")
        return quantized_model
    
    def prune(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
    ) -> Any:
        """
        Apply PyTorch pruning.
        """
        import torch
        import torch.nn.utils.prune as prune
        
        logger.info("Applying PyTorch pruning")
        
        # Apply L1 unstructured pruning to all Conv2d and Linear layers
        pruning_amount = 0.3  # Prune 30% by default
        
        for name, module in model.named_modules():
            if isinstance(module, (torch.nn.Conv2d, torch.nn.Linear)):
                prune.l1_unstructured(module, name='weight', amount=pruning_amount)
                # Make pruning permanent
                prune.remove(module, 'weight')
        
        logger.info(f"PyTorch pruning complete ({pruning_amount:.0%} sparsity)")
        return model
    
    def optimize_graph(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
    ) -> Any:
        """
        Apply PyTorch graph optimizations (fusion, etc.).
        """
        import torch
        
        logger.info("Applying PyTorch graph optimizations")
        
        model.eval()
        
        # JIT trace for optimization
        if input_shape:
            dummy_input = torch.randn(*input_shape)
            traced_model = torch.jit.trace(model, dummy_input)
            # Freeze to enable optimizations
            traced_model = torch.jit.freeze(traced_model)
            logger.info("PyTorch JIT optimization complete")
            return traced_model
        else:
            logger.warning("No input shape provided, skipping JIT optimization")
            return model
    
    def save_model(self, model: Any, path: Path) -> None:
        """Save PyTorch model."""
        import torch
        
        # Handle both regular and JIT models
        if isinstance(model, torch.jit.ScriptModule):
            torch.jit.save(model, str(path))
        else:
            torch.save(model.state_dict(), str(path))
    
    def load_model(self, path: Path) -> Any:
        """Load PyTorch model."""
        import torch
        
        # Try loading as JIT model first
        try:
            return torch.jit.load(str(path))
        except:
            # Load as state dict
            return torch.load(str(path))
    
    def get_capabilities(self) -> List[str]:
        return ['quantize', 'prune', 'graph_optimization']
