"""
AI Training Module Exports

This module exports AI training classes and utilities.
Part of Sprint 9.5 Advanced Machine Learning & Training development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

from .training_manager import (
    TrainingManager,
    TrainingJob,
    TrainingConfig,
    ExperimentConfig,
    TrainingStatus,
    TrainingMode,
    OptimizationStrategy
)

__all__ = [
    'TrainingManager',
    'TrainingJob',
    'TrainingConfig',
    'ExperimentConfig',
    'TrainingStatus',
    'TrainingMode',
    'OptimizationStrategy'
]

__version__ = "9.5.0"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.5 - Advanced Machine Learning & Training"
