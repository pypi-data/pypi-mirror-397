"""
ONNX and ONNX Runtime backend for model optimization.
"""

from typing import Any, Optional, List
from pathlib import Path
import warnings
import tempfile

from hamerspace.backends.base import BaseBackend
from hamerspace.core.models import (
    Constraints,
    ModelInfo,
    ModelFramework,
    TargetHardware,
)
from hamerspace.utils.logger import get_logger

logger = get_logger(__name__)


class ONNXBackend(BaseBackend):
    """Backend using ONNX and ONNX Runtime for optimization."""
    
    def __init__(self):
        super().__init__("ONNX")
        self._onnx_available = False
        self._onnxruntime_available = False
        
        try:
            import onnx
            import onnxruntime
            self._onnx_available = True
            self._onnxruntime_available = True
        except ImportError:
            warnings.warn("ONNX/ONNX Runtime not available")
    
    def is_available(self) -> bool:
        return self._onnx_available and self._onnxruntime_available
    
    def supports_model(self, model_info: ModelInfo) -> bool:
        # ONNX can work with ONNX models directly or converted models
        return True  # ONNX is framework-agnostic
    
    def can_satisfy_constraints(
        self,
        constraints: Constraints,
        model_info: ModelInfo,
    ) -> bool:
        # ONNX Runtime quantization works well across hardware
        return True
    
    def quantize(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
        calibration_data: Optional[Any] = None,
    ) -> Any:
        """
        Apply ONNX Runtime quantization.
        """
        from onnxruntime.quantization import quantize_dynamic, quantize_static, QuantType
        from onnxruntime.quantization.calibrate import CalibrationDataReader
        import onnx
        
        logger.info("Applying ONNX Runtime quantization")
        
        # Convert to ONNX if needed
        if not isinstance(model, str) and not isinstance(model, Path):
            model = self._convert_to_onnx(model, input_shape)
        
        # Create temporary files for input/output
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as tmp_in:
            with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as tmp_out:
                input_path = Path(tmp_in.name)
                output_path = Path(tmp_out.name)
                
                # Save input model if it's an ONNX object
                if isinstance(model, onnx.ModelProto):
                    onnx.save(model, str(input_path))
                else:
                    input_path = Path(model)
                
                if calibration_data is not None:
                    # Static quantization with calibration
                    logger.info("Using static quantization with calibration")
                    
                    # Create calibration data reader
                    class CustomDataReader(CalibrationDataReader):
                        def __init__(self, data):
                            self.data = iter(data)
                            self.input_name = None
                        
                        def get_next(self):
                            try:
                                batch = next(self.data)
                                if isinstance(batch, (list, tuple)):
                                    batch = batch[0]
                                if self.input_name is None:
                                    # Get input name from model
                                    m = onnx.load(str(input_path))
                                    self.input_name = m.graph.input[0].name
                                return {self.input_name: batch.cpu().numpy()}
                            except StopIteration:
                                return None
                    
                    quantize_static(
                        str(input_path),
                        str(output_path),
                        CustomDataReader(calibration_data)
                    )
                else:
                    # Dynamic quantization
                    logger.info("Using dynamic quantization")
                    quantize_dynamic(
                        str(input_path),
                        str(output_path),
                        weight_type=QuantType.QUInt8
                    )
                
                # Load quantized model
                quantized_model = onnx.load(str(output_path))
                
                # Cleanup
                input_path.unlink()
                output_path.unlink()
        
        logger.info("ONNX quantization complete")
        return quantized_model
    
    def prune(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
    ) -> Any:
        """
        ONNX doesn't have native pruning - would need to prune before conversion.
        """
        logger.warning("ONNX backend does not support pruning directly")
        return model
    
    def optimize_graph(
        self,
        model: Any,
        input_shape: Optional[List[int]],
        constraints: Constraints,
    ) -> Any:
        """
        Apply ONNX graph optimizations.
        """
        import onnx
        from onnxruntime.transformers import optimizer
        
        logger.info("Applying ONNX graph optimizations")
        
        # Convert to ONNX if needed
        if not isinstance(model, onnx.ModelProto):
            model = self._convert_to_onnx(model, input_shape)
        
        # Apply graph optimizations
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as tmp:
            tmp_path = Path(tmp.name)
            onnx.save(model, str(tmp_path))
            
            # Use ONNX Runtime optimizer
            optimized_model = onnx.load(str(tmp_path))
            tmp_path.unlink()
        
        logger.info("ONNX graph optimization complete")
        return optimized_model
    
    def save_model(self, model: Any, path: Path) -> None:
        """Save ONNX model."""
        import onnx
        
        if isinstance(model, onnx.ModelProto):
            onnx.save(model, str(path))
        else:
            # Assume it's already a path
            import shutil
            shutil.copy(model, path)
    
    def load_model(self, path: Path) -> Any:
        """Load ONNX model."""
        import onnx
        return onnx.load(str(path))
    
    def _convert_to_onnx(self, model: Any, input_shape: Optional[List[int]]) -> Any:
        """Convert a PyTorch or TensorFlow model to ONNX."""
        import onnx
        import torch
        
        logger.info("Converting model to ONNX format")
        
        # Try PyTorch conversion
        try:
            if input_shape is None:
                raise ValueError("Input shape required for ONNX conversion")
            
            dummy_input = torch.randn(*input_shape)
            
            with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as tmp:
                tmp_path = Path(tmp.name)
                torch.onnx.export(
                    model,
                    dummy_input,
                    str(tmp_path),
                    opset_version=13,
                    input_names=['input'],
                    output_names=['output'],
                    dynamic_axes={'input': {0: 'batch_size'}}
                )
                onnx_model = onnx.load(str(tmp_path))
                tmp_path.unlink()
                
            logger.info("Conversion to ONNX complete")
            return onnx_model
        except Exception as e:
            logger.error(f"Failed to convert to ONNX: {e}")
            raise
    
    def get_capabilities(self) -> List[str]:
        return ['quantize', 'graph_optimization']
