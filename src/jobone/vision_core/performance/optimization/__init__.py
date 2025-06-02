"""
Performance Optimization Module Exports

This module exports optimization classes and utilities.
Part of Sprint 9.8 Advanced Performance & Optimization development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

# Legacy optimizer (Sprint 9.2)
from .performance_optimizer import (
    PerformanceOptimizer,
    OptimizationRule,
    OptimizationLevel,
    OptimizationType
)

# Advanced optimization engine (Sprint 9.8)
from .optimization_engine import (
    OptimizationEngine,
    OptimizationProfile,
    OptimizationResult,
    SystemProfile,
    OptimizationTarget,
    OptimizationMode,
    OptimizationPhase
)

__all__ = [
    # Legacy (Sprint 9.2)
    'PerformanceOptimizer',
    'OptimizationRule',
    'OptimizationLevel',
    'OptimizationType',

    # Advanced (Sprint 9.8)
    'OptimizationEngine',
    'OptimizationProfile',
    'OptimizationResult',
    'SystemProfile',
    'OptimizationTarget',
    'OptimizationMode',
    'OptimizationPhase'
]

__version__ = "9.8.0"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.8 - Advanced Performance & Optimization"
