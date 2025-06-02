"""
AI Inference Module Exports

This module exports AI inference classes and utilities.
Part of Sprint 9.4 Advanced AI Integration & Machine Learning development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

from .inference_engine import (
    InferenceEngine,
    InferenceRequest,
    InferenceResult,
    InferenceCache,
    BatchConfig,
    InferenceMode,
    InferenceDevice,
    InferenceStatus
)

__all__ = [
    'InferenceEngine',
    'InferenceRequest',
    'InferenceResult',
    'InferenceCache',
    'BatchConfig',
    'InferenceMode',
    'InferenceDevice',
    'InferenceStatus'
]

__version__ = "9.4.0"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.4 - Advanced AI Integration & Machine Learning"
