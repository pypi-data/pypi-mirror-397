"""
Benchmarker for measuring model performance metrics.
"""

import time
import tempfile
from pathlib import Path
from typing import Any, Optional, List
import psutil

from hamerspace.core.models import ModelInfo, ModelMetrics, ModelFramework
from hamerspace.utils.logger import get_logger

logger = get_logger(__name__)


class Benchmarker:
    """
    Benchmarks models to measure size, latency, and memory usage.
    """
    
    def benchmark_model(
        self,
        model: Any,
        model_info: ModelInfo,
        target_hardware: str,
        input_shape: Optional[List[int]] = None,
        batch_size: int = 1,
        num_runs: int = 100,
    ) -> ModelMetrics:
        """
        Benchmark a model.
        
        Args:
            model: Model to benchmark
            model_info: Model information
            target_hardware: Target hardware (cpu, gpu, etc.)
            input_shape: Input tensor shape
            batch_size: Batch size for inference
            num_runs: Number of runs for latency measurement
        
        Returns:
            ModelMetrics with benchmarking results
        """
        logger.info(f"Benchmarking model on {target_hardware}")
        
        # Measure size
        size_mb = self._measure_size(model, model_info)
        
        # Measure latency
        latency_ms, memory_mb = self._measure_latency_and_memory(
            model,
            model_info,
            input_shape,
            batch_size,
            num_runs,
            target_hardware,
        )
        
        # Calculate throughput
        throughput = 1000.0 / latency_ms if latency_ms > 0 else 0
        
        metrics = ModelMetrics(
            size_mb=size_mb,
            latency_ms=latency_ms,
            memory_mb=memory_mb,
            throughput=throughput,
        )
        
        logger.info(f"Benchmark complete: {metrics}")
        return metrics
    
    def _measure_size(self, model: Any, model_info: ModelInfo) -> float:
        """Measure model size in MB."""
        try:
            # Save model to temporary file and measure
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = Path(tmp.name)
                
                if model_info.framework == ModelFramework.PYTORCH:
                    import torch
                    if isinstance(model, torch.jit.ScriptModule):
                        torch.jit.save(model, str(tmp_path))
                    else:
                        torch.save(model.state_dict(), str(tmp_path))
                
                elif model_info.framework == ModelFramework.TENSORFLOW:
                    model.save(str(tmp_path))
                
                elif model_info.framework == ModelFramework.ONNX:
                    import onnx
                    onnx.save(model, str(tmp_path))
                
                else:
                    # Fallback: estimate from parameters
                    if model_info.num_parameters:
                        # Assume 4 bytes per parameter (float32)
                        return (model_info.num_parameters * 4) / (1024 * 1024)
                    return 0.0
                
                size_bytes = tmp_path.stat().st_size
                tmp_path.unlink()
                
                return size_bytes / (1024 * 1024)  # Convert to MB
        
        except Exception as e:
            logger.warning(f"Could not measure model size: {e}")
            # Fallback estimate
            if model_info.num_parameters:
                return (model_info.num_parameters * 4) / (1024 * 1024)
            return 0.0
    
    def _measure_latency_and_memory(
        self,
        model: Any,
        model_info: ModelInfo,
        input_shape: Optional[List[int]],
        batch_size: int,
        num_runs: int,
        target_hardware: str,
    ) -> tuple[float, float]:
        """
        Measure inference latency and memory usage.
        
        Returns:
            (latency_ms, memory_mb)
        """
        if input_shape is None:
            logger.warning("No input shape provided, cannot measure latency")
            return 0.0, 0.0
        
        try:
            if model_info.framework == ModelFramework.PYTORCH:
                return self._benchmark_pytorch(
                    model, input_shape, batch_size, num_runs, target_hardware
                )
            
            elif model_info.framework == ModelFramework.TENSORFLOW:
                return self._benchmark_tensorflow(
                    model, input_shape, batch_size, num_runs
                )
            
            elif model_info.framework == ModelFramework.ONNX:
                return self._benchmark_onnx(
                    model, input_shape, batch_size, num_runs
                )
            
            else:
                logger.warning(f"Cannot benchmark {model_info.framework}")
                return 0.0, 0.0
        
        except Exception as e:
            logger.warning(f"Latency measurement failed: {e}")
            return 0.0, 0.0
    
    def _benchmark_pytorch(
        self,
        model: Any,
        input_shape: List[int],
        batch_size: int,
        num_runs: int,
        target_hardware: str,
    ) -> tuple[float, float]:
        """Benchmark PyTorch model."""
        import torch
        
        # Set device
        device = 'cpu'
        if target_hardware.lower() in ['gpu', 'cuda'] and torch.cuda.is_available():
            device = 'cuda'
        
        model = model.to(device)
        model.eval()
        
        # Create dummy input
        input_shape_with_batch = [batch_size] + input_shape[1:]
        dummy_input = torch.randn(*input_shape_with_batch).to(device)
        
        # Warmup
        with torch.no_grad():
            for _ in range(10):
                _ = model(dummy_input)
        
        # Measure memory before
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Measure latency
        latencies = []
        with torch.no_grad():
            for _ in range(num_runs):
                start = time.perf_counter()
                _ = model(dummy_input)
                if device == 'cuda':
                    torch.cuda.synchronize()
                end = time.perf_counter()
                latencies.append((end - start) * 1000)  # Convert to ms
        
        # Measure memory after
        mem_after = process.memory_info().rss / (1024 * 1024)  # MB
        memory_mb = mem_after - mem_before
        
        # Calculate average latency
        avg_latency = sum(latencies) / len(latencies)
        
        return avg_latency, max(0, memory_mb)
    
    def _benchmark_tensorflow(
        self,
        model: Any,
        input_shape: List[int],
        batch_size: int,
        num_runs: int,
    ) -> tuple[float, float]:
        """Benchmark TensorFlow model."""
        import tensorflow as tf
        import numpy as np
        
        # Create dummy input
        input_shape_with_batch = [batch_size] + input_shape[1:]
        dummy_input = np.random.randn(*input_shape_with_batch).astype(np.float32)
        
        # Warmup
        for _ in range(10):
            _ = model(dummy_input, training=False)
        
        # Measure memory before
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Measure latency
        latencies = []
        for _ in range(num_runs):
            start = time.perf_counter()
            _ = model(dummy_input, training=False)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms
        
        # Measure memory after
        mem_after = process.memory_info().rss / (1024 * 1024)  # MB
        memory_mb = mem_after - mem_before
        
        avg_latency = sum(latencies) / len(latencies)
        
        return avg_latency, max(0, memory_mb)
    
    def _benchmark_onnx(
        self,
        model: Any,
        input_shape: List[int],
        batch_size: int,
        num_runs: int,
    ) -> tuple[float, float]:
        """Benchmark ONNX model."""
        import onnxruntime as ort
        import numpy as np
        import onnx
        
        # Create inference session
        if isinstance(model, onnx.ModelProto):
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as tmp:
                tmp_path = Path(tmp.name)
                onnx.save(model, str(tmp_path))
                session = ort.InferenceSession(str(tmp_path))
                tmp_path.unlink()
        else:
            session = ort.InferenceSession(str(model))
        
        # Get input name
        input_name = session.get_inputs()[0].name
        
        # Create dummy input
        input_shape_with_batch = [batch_size] + input_shape[1:]
        dummy_input = np.random.randn(*input_shape_with_batch).astype(np.float32)
        
        # Warmup
        for _ in range(10):
            _ = session.run(None, {input_name: dummy_input})
        
        # Measure memory before
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Measure latency
        latencies = []
        for _ in range(num_runs):
            start = time.perf_counter()
            _ = session.run(None, {input_name: dummy_input})
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms
        
        # Measure memory after
        mem_after = process.memory_info().rss / (1024 * 1024)  # MB
        memory_mb = mem_after - mem_before
        
        avg_latency = sum(latencies) / len(latencies)
        
        return avg_latency, max(0, memory_mb)
