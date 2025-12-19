"""
Hamerspace: Model Compression and Optimization Engine

A compiler-style optimization pass for non-LLM machine learning models.
"""

from hamerspace.core.optimizer import Optimizer
from hamerspace.core.constraints import Constraints
from hamerspace.core.goals import OptimizationGoal
from hamerspace.core.result import OptimizationResult
from hamerspace.core.backends import Backend

__version__ = "0.1.0"
__all__ = [
    "Optimizer",
    "Constraints",
    "OptimizationGoal",
    "OptimizationResult",
    "Backend",
]
