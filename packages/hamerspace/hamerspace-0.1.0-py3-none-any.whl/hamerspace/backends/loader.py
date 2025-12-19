"""
Model loader for different frameworks.
"""

from pathlib import Path
from typing import Any, Tuple, Optional, List
import warnings

from hamerspace.core.models import ModelInfo, ModelFramework
from hamerspace.utils.logger import get_logger

logger = get_logger(__name__)


class ModelLoader:
    """Loads models from different frameworks."""
    
    def load_pytorch(
        self,
        model_path: Any,
        input_shape: Optional[List[int]] = None,
    ) -> Tuple[Any, ModelInfo]:
        """
        Load PyTorch model.
        
        Args:
            model_path: Path to .pt/.pth file or model object
            input_shape: Input shape
        
        Returns:
            (model, model_info)
        """
        import torch
        
        # If it's already a model object, use it
        if isinstance(model_path, torch.nn.Module):
            model = model_path
            logger.info("Using provided PyTorch model object")
        else:
            # Load from file
            path = Path(model_path)
            logger.info(f"Loading PyTorch model from {path}")
            
            if not path.exists():
                raise FileNotFoundError(f"Model file not found: {path}")
            
            # Try loading as full model first
            try:
                model = torch.load(str(path))
                if not isinstance(model, torch.nn.Module):
                    raise ValueError("Loaded object is not a PyTorch model")
            except:
                # Try loading as state dict
                logger.warning("Could not load as full model, trying as state dict")
                raise ValueError(
                    "Please provide a full model or instantiated model object"
                )
        
        # Extract model info
        model.eval()
        num_params = sum(p.numel() for p in model.parameters())
        
        model_info = ModelInfo(
            framework=ModelFramework.PYTORCH,
            input_shape=input_shape,
            num_parameters=num_params,
        )
        
        logger.info(f"Loaded PyTorch model: {num_params:,} parameters")
        return model, model_info
    
    def load_tensorflow(
        self,
        model_path: Path,
        input_shape: Optional[List[int]] = None,
    ) -> Tuple[Any, ModelInfo]:
        """
        Load TensorFlow model.
        
        Args:
            model_path: Path to .h5 or SavedModel directory
            input_shape: Input shape
        
        Returns:
            (model, model_info)
        """
        import tensorflow as tf
        
        path = Path(model_path)
        logger.info(f"Loading TensorFlow model from {path}")
        
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        # Load model
        if path.is_dir():
            # SavedModel format
            model = tf.keras.models.load_model(str(path))
        else:
            # HDF5 format
            model = tf.keras.models.load_model(str(path))
        
        # Extract model info
        num_params = model.count_params()
        
        # Try to get input shape from model
        if input_shape is None and hasattr(model, 'input_shape'):
            input_shape = list(model.input_shape)
        
        model_info = ModelInfo(
            framework=ModelFramework.TENSORFLOW,
            input_shape=input_shape,
            num_parameters=num_params,
        )
        
        logger.info(f"Loaded TensorFlow model: {num_params:,} parameters")
        return model, model_info
    
    def load_onnx(
        self,
        model_path: Path,
    ) -> Tuple[Any, ModelInfo]:
        """
        Load ONNX model.
        
        Args:
            model_path: Path to .onnx file
        
        Returns:
            (model, model_info)
        """
        import onnx
        
        path = Path(model_path)
        logger.info(f"Loading ONNX model from {path}")
        
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        # Load ONNX model
        model = onnx.load(str(path))
        
        # Extract model info
        input_shape = None
        if model.graph.input:
            input_tensor = model.graph.input[0]
            if input_tensor.type.tensor_type.shape.dim:
                input_shape = [
                    dim.dim_value for dim in input_tensor.type.tensor_type.shape.dim
                ]
        
        # Count parameters (roughly)
        num_params = 0
        for initializer in model.graph.initializer:
            param_size = 1
            for dim in initializer.dims:
                param_size *= dim
            num_params += param_size
        
        model_info = ModelInfo(
            framework=ModelFramework.ONNX,
            input_shape=input_shape,
            num_parameters=num_params,
        )
        
        logger.info(f"Loaded ONNX model: {num_params:,} parameters")
        return model, model_info
