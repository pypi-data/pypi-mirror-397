"""
Unit tests for Hamerspace.
"""

import pytest
import torch
import torch.nn as nn
from pathlib import Path

from hamerspace import Optimizer, OptimizationGoal, Constraints, Backend
from hamerspace.core.models import ModelInfo, ModelFramework


class SimpleModel(nn.Module):
    """Simple model for testing."""
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 20)
        self.fc2 = nn.Linear(20, 5)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x


class TestOptimizer:
    """Test the main Optimizer class."""
    
    def test_from_pytorch_model(self):
        """Test loading PyTorch model."""
        model = SimpleModel()
        model.eval()
        
        optimizer = Optimizer.from_pytorch(
            model,
            input_shape=[1, 10]
        )
        
        assert optimizer is not None
        assert optimizer.model_info.framework == ModelFramework.PYTORCH
    
    def test_benchmark(self):
        """Test benchmarking."""
        model = SimpleModel()
        model.eval()
        
        optimizer = Optimizer.from_pytorch(
            model,
            input_shape=[1, 10]
        )
        
        metrics = optimizer.benchmark(
            hardware="cpu",
            num_runs=10,
            batch_size=1
        )
        
        assert metrics.size_mb > 0
        assert metrics.latency_ms > 0
    
    def test_quantize_optimization(self):
        """Test quantization optimization."""
        model = SimpleModel()
        model.eval()
        
        optimizer = Optimizer.from_pytorch(
            model,
            input_shape=[1, 10]
        )
        
        constraints = Constraints(
            target_size_mb=1,
            target_hardware="cpu"
        )
        
        result = optimizer.optimize(
            goal=OptimizationGoal.QUANTIZE,
            constraints=constraints
        )
        
        assert result is not None
        assert result.report.size_reduction_ratio > 0


class TestConstraints:
    """Test Constraints model."""
    
    def test_valid_constraints(self):
        """Test creating valid constraints."""
        constraints = Constraints(
            target_size_mb=10,
            max_latency_ms=50,
            max_accuracy_drop=0.05
        )
        
        assert constraints.target_size_mb == 10
        assert constraints.max_latency_ms == 50
        assert constraints.max_accuracy_drop == 0.05
    
    def test_constraint_checks(self):
        """Test constraint helper methods."""
        constraints = Constraints(
            target_size_mb=10,
            max_latency_ms=50
        )
        
        assert constraints.has_size_constraint()
        assert constraints.has_latency_constraint()
        assert not constraints.has_accuracy_constraint()
    
    def test_invalid_accuracy_drop(self):
        """Test invalid accuracy drop raises error."""
        with pytest.raises(ValueError):
            Constraints(max_accuracy_drop=1.5)  # > 1.0


class TestBackends:
    """Test backend availability."""
    
    def test_pytorch_backend_available(self):
        """Test PyTorch backend."""
        from hamerspace.backends.pytorch_backend import PyTorchBackend
        
        backend = PyTorchBackend()
        assert backend.is_available()  # Should be available in test env
    
    def test_backend_capabilities(self):
        """Test backend capability reporting."""
        from hamerspace.backends.pytorch_backend import PyTorchBackend
        
        backend = PyTorchBackend()
        capabilities = backend.get_capabilities()
        
        assert 'quantize' in capabilities


class TestStrategySelector:
    """Test strategy selection."""
    
    def test_select_quantization_strategy(self):
        """Test selecting quantization strategy."""
        from hamerspace.strategies.strategy_selector import StrategySelector
        from hamerspace.core.models import ModelMetrics
        
        model = SimpleModel()
        model_info = ModelInfo(
            framework=ModelFramework.PYTORCH,
            input_shape=[1, 10],
            num_parameters=250
        )
        
        constraints = Constraints(
            target_size_mb=0.5,
            target_hardware="cpu"
        )
        
        original_metrics = ModelMetrics(
            size_mb=1.0,
            latency_ms=10.0
        )
        
        selector = StrategySelector()
        strategy = selector.select_strategy(
            goal=OptimizationGoal.QUANTIZE,
            constraints=constraints,
            model_info=model_info,
            original_metrics=original_metrics
        )
        
        assert strategy is not None
        assert strategy.config.goal == OptimizationGoal.QUANTIZE


class TestBenchmarker:
    """Test benchmarking functionality."""
    
    def test_benchmark_pytorch_model(self):
        """Test benchmarking PyTorch model."""
        from hamerspace.benchmarks.benchmarker import Benchmarker
        
        model = SimpleModel()
        model.eval()
        
        model_info = ModelInfo(
            framework=ModelFramework.PYTORCH,
            num_parameters=250
        )
        
        benchmarker = Benchmarker()
        metrics = benchmarker.benchmark_model(
            model=model,
            model_info=model_info,
            target_hardware="cpu",
            input_shape=[1, 10],
            batch_size=1,
            num_runs=10
        )
        
        assert metrics.size_mb > 0
        assert metrics.latency_ms > 0


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_full_optimization_pipeline(self):
        """Test complete optimization pipeline."""
        # Create model
        model = SimpleModel()
        model.eval()
        
        # Initialize optimizer
        optimizer = Optimizer.from_pytorch(
            model,
            input_shape=[1, 10]
        )
        
        # Define constraints
        constraints = Constraints(
            target_size_mb=0.5,
            max_latency_ms=5,
            target_hardware="cpu"
        )
        
        # Optimize
        result = optimizer.optimize(
            goal=OptimizationGoal.QUANTIZE,
            constraints=constraints
        )
        
        # Verify result
        assert result is not None
        assert result.optimized_model is not None
        assert result.report is not None
        assert result.report.size_reduction_ratio > 0
        
        # Test saving
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "optimized.pt"
            result.save_model(model_path)
            assert model_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
