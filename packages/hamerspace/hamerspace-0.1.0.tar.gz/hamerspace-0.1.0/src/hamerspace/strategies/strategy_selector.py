"""
Strategy selector that chooses the best optimization approach.
"""

from typing import Optional, List

from hamerspace.core.models import (
    OptimizationGoal,
    Backend,
    Constraints,
    ModelInfo,
    ModelMetrics,
    OptimizationConfig,
)
from hamerspace.strategies.strategy import (
    OptimizationStrategy,
    QuantizationStrategy,
    PruningStrategy,
    GraphOptimizationStrategy,
    CompositeStrategy,
)
from hamerspace.backends.pytorch_backend import PyTorchBackend
from hamerspace.backends.onnx_backend import ONNXBackend
from hamerspace.backends.openvino_backend import OpenVINOBackend
from hamerspace.utils.logger import get_logger

logger = get_logger(__name__)


class StrategySelector:
    """
    Selects the optimal optimization strategy based on:
    - User's optimization goal
    - Model characteristics
    - Target constraints
    - Available backends
    """
    
    def __init__(self):
        # Initialize all available backends
        self.backends = [
            PyTorchBackend(),
            ONNXBackend(),
            OpenVINOBackend(),
        ]
        
        # Filter to only available backends
        self.available_backends = [
            b for b in self.backends if b.is_available()
        ]
        
        if not self.available_backends:
            raise RuntimeError("No optimization backends available!")
        
        logger.info(
            f"Available backends: {[b.name for b in self.available_backends]}"
        )
    
    def select_strategy(
        self,
        goal: OptimizationGoal,
        constraints: Constraints,
        model_info: ModelInfo,
        original_metrics: ModelMetrics,
        preferred_backends: Optional[List[Backend]] = None,
    ) -> OptimizationStrategy:
        """
        Select the best optimization strategy.
        
        Args:
            goal: Optimization goal
            constraints: User constraints
            model_info: Information about the model
            original_metrics: Original model metrics
            preferred_backends: Preferred backends (optional)
        
        Returns:
            Selected optimization strategy
        """
        logger.info(f"Selecting strategy for goal: {goal.value}")
        
        # Filter backends by preference and capability
        candidate_backends = self._filter_backends(
            model_info,
            constraints,
            preferred_backends,
        )
        
        if not candidate_backends:
            raise ValueError(
                "No backends available that support this model and constraints"
            )
        
        # Generate candidate strategies
        if goal == OptimizationGoal.AUTO:
            strategies = self._generate_auto_strategies(
                candidate_backends,
                constraints,
                original_metrics,
            )
        elif goal == OptimizationGoal.QUANTIZE:
            strategies = self._generate_quantization_strategies(
                candidate_backends,
            )
        elif goal == OptimizationGoal.PRUNE:
            strategies = self._generate_pruning_strategies(
                candidate_backends,
            )
        elif goal == OptimizationGoal.DISTILL:
            raise NotImplementedError(
                "Knowledge distillation requires training loop - not yet implemented"
            )
        else:
            raise ValueError(f"Unknown optimization goal: {goal}")
        
        # Select best strategy
        best_strategy = self._rank_strategies(
            strategies,
            constraints,
            original_metrics,
        )
        
        logger.info(
            f"Selected: {best_strategy.config.technique} "
            f"via {best_strategy.backend.name}"
        )
        
        return best_strategy
    
    def _filter_backends(
        self,
        model_info: ModelInfo,
        constraints: Constraints,
        preferred_backends: Optional[List[Backend]],
    ) -> List:
        """Filter backends by capability and preference."""
        candidates = []
        
        for backend in self.available_backends:
            # Check if backend supports this model
            if not backend.supports_model(model_info):
                logger.debug(f"{backend.name} does not support this model")
                continue
            
            # Check if backend can potentially satisfy constraints
            if not backend.can_satisfy_constraints(constraints, model_info):
                logger.debug(f"{backend.name} unlikely to satisfy constraints")
                continue
            
            candidates.append(backend)
        
        # Apply preference ordering if specified
        if preferred_backends:
            backend_map = {Backend[b.name.upper()]: b for b in candidates}
            ordered = []
            for pref in preferred_backends:
                if pref in backend_map:
                    ordered.append(backend_map[pref])
            # Add remaining candidates
            for backend in candidates:
                if backend not in ordered:
                    ordered.append(backend)
            candidates = ordered
        
        return candidates
    
    def _generate_auto_strategies(
        self,
        backends: List,
        constraints: Constraints,
        original_metrics: ModelMetrics,
    ) -> List[OptimizationStrategy]:
        """
        Generate candidate strategies for AUTO mode.
        
        AUTO mode tries to intelligently select the best approach
        based on constraints.
        """
        strategies = []
        
        # If size is the main constraint, prioritize quantization
        if constraints.has_size_constraint():
            strategies.extend(self._generate_quantization_strategies(backends))
        
        # If latency is critical, add graph optimization
        if constraints.has_latency_constraint():
            for backend in backends:
                config = OptimizationConfig(
                    goal=OptimizationGoal.AUTO,
                    backend=Backend[backend.name.upper()],
                    technique="graph_optimization",
                )
                strategies.append(
                    GraphOptimizationStrategy(config, backend)
                )
        
        # Add composite strategies (quantization + graph optimization)
        for backend in backends:
            if 'quantize' in backend.get_capabilities():
                quant_config = OptimizationConfig(
                    goal=OptimizationGoal.QUANTIZE,
                    backend=Backend[backend.name.upper()],
                    technique="int8_quantization",
                )
                graph_config = OptimizationConfig(
                    goal=OptimizationGoal.AUTO,
                    backend=Backend[backend.name.upper()],
                    technique="graph_optimization",
                )
                
                composite_config = OptimizationConfig(
                    goal=OptimizationGoal.AUTO,
                    backend=Backend[backend.name.upper()],
                    technique="quantization+graph_opt",
                )
                
                strategies.append(
                    CompositeStrategy(
                        composite_config,
                        [
                            QuantizationStrategy(quant_config, backend),
                            GraphOptimizationStrategy(graph_config, backend),
                        ]
                    )
                )
        
        return strategies
    
    def _generate_quantization_strategies(
        self,
        backends: List,
    ) -> List[OptimizationStrategy]:
        """Generate quantization strategies."""
        strategies = []
        
        for backend in backends:
            if 'quantize' not in backend.get_capabilities():
                continue
            
            # INT8 quantization
            config = OptimizationConfig(
                goal=OptimizationGoal.QUANTIZE,
                backend=Backend[backend.name.upper()],
                technique="int8_quantization",
            )
            strategies.append(QuantizationStrategy(config, backend))
            
            # Dynamic quantization (fallback)
            config_dynamic = OptimizationConfig(
                goal=OptimizationGoal.QUANTIZE,
                backend=Backend[backend.name.upper()],
                technique="dynamic_quantization",
            )
            strategies.append(QuantizationStrategy(config_dynamic, backend))
        
        return strategies
    
    def _generate_pruning_strategies(
        self,
        backends: List,
    ) -> List[OptimizationStrategy]:
        """Generate pruning strategies."""
        strategies = []
        
        for backend in backends:
            if 'prune' not in backend.get_capabilities():
                continue
            
            config = OptimizationConfig(
                goal=OptimizationGoal.PRUNE,
                backend=Backend[backend.name.upper()],
                technique="l1_unstructured_pruning",
            )
            strategies.append(PruningStrategy(config, backend))
        
        return strategies
    
    def _rank_strategies(
        self,
        strategies: List[OptimizationStrategy],
        constraints: Constraints,
        original_metrics: ModelMetrics,
    ) -> OptimizationStrategy:
        """
        Rank strategies and select the best one.
        
        Ranking is based on:
        1. Likelihood of satisfying constraints
        2. Expected performance improvement
        3. Backend reliability
        """
        if not strategies:
            raise ValueError("No viable strategies available")
        
        ranked = []
        
        for strategy in strategies:
            # Estimate impact
            est_size, est_latency = strategy.estimate_impact(
                original_metrics.size_mb,
                original_metrics.latency_ms,
            )
            
            # Calculate score
            score = 0
            
            # Check constraint satisfaction (most important)
            satisfies_constraints = True
            
            if constraints.has_size_constraint():
                if est_size <= constraints.target_size_mb:
                    score += 100
                else:
                    satisfies_constraints = False
                    score -= 50
            
            if constraints.has_latency_constraint():
                if est_latency <= constraints.max_latency_ms:
                    score += 100
                else:
                    satisfies_constraints = False
                    score -= 50
            
            # Reward better compression ratios
            size_reduction = 1 - (est_size / original_metrics.size_mb)
            latency_improvement = 1 - (est_latency / original_metrics.latency_ms)
            
            score += size_reduction * 50
            score += latency_improvement * 30
            
            # Prefer composite strategies if they satisfy constraints
            if isinstance(strategy, CompositeStrategy) and satisfies_constraints:
                score += 20
            
            ranked.append((score, strategy))
            
            logger.debug(
                f"Strategy {strategy.config.technique}: "
                f"score={score:.1f}, est_size={est_size:.1f}MB, "
                f"est_latency={est_latency:.1f}ms"
            )
        
        # Sort by score (descending)
        ranked.sort(key=lambda x: x[0], reverse=True)
        
        return ranked[0][1]
