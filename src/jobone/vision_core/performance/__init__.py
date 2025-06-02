"""
Performance Module Exports

This module exports all performance classes and utilities.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

# Core performance classes (Sprint 9.8)
from .core import (
    PerformanceManager,
    PerformanceMetrics,
    OptimizationTask,
    ResourceLimit,
    PerformanceLevel,
    OptimizationStrategy,
    ResourceType
)

# Advanced caching classes (Sprint 9.8)
from .caching import (
    CacheManager as AdvancedCacheManager,
    CacheConfig,
    CacheEntry as AdvancedCacheEntry,
    CacheStats,
    CacheStrategy,
    CacheLevel as AdvancedCacheLevel,
    CacheStatus
)

# Legacy cache classes (Sprint 9.2)
from .cache import (
    CacheManager,
    CacheEntry,
    CacheLevel,
    CachePolicy
)

# Optimization classes
from .optimization import (
    # Advanced (Sprint 9.8)
    OptimizationEngine,
    OptimizationProfile,
    OptimizationResult,
    SystemProfile,
    OptimizationTarget,
    OptimizationMode,
    OptimizationPhase,
    # Legacy (Sprint 9.2)
    PerformanceOptimizer,
    OptimizationRule,
    OptimizationLevel,
    OptimizationType
)

__all__ = [
    # Core Performance (Sprint 9.8)
    'PerformanceManager',
    'PerformanceMetrics',
    'OptimizationTask',
    'ResourceLimit',
    'PerformanceLevel',
    'OptimizationStrategy',
    'ResourceType',

    # Advanced Caching (Sprint 9.8)
    'AdvancedCacheManager',
    'CacheConfig',
    'AdvancedCacheEntry',
    'CacheStats',
    'CacheStrategy',
    'AdvancedCacheLevel',
    'CacheStatus',

    # Legacy Cache (Sprint 9.2)
    'CacheManager',
    'CacheEntry',
    'CacheLevel',
    'CachePolicy',

    # Advanced Optimization (Sprint 9.8)
    'OptimizationEngine',
    'OptimizationProfile',
    'OptimizationResult',
    'SystemProfile',
    'OptimizationTarget',
    'OptimizationMode',
    'OptimizationPhase',

    # Legacy Optimization (Sprint 9.2)
    'PerformanceOptimizer',
    'OptimizationRule',
    'OptimizationLevel',
    'OptimizationType'
]

__version__ = "9.8.0"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.8 - Advanced Performance & Optimization"
