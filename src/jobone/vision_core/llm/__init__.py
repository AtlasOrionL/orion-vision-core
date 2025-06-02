#!/usr/bin/env python3
"""
Orion Vision Core LLM Module
Sprint 8.2 - Advanced LLM Management and Core "Brain" AI Capabilities
Orion Vision Core - Autonomous AI Operating System

This module provides advanced LLM management capabilities including
multi-provider API management, intelligent model selection, and
performance optimization for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.2.0
Date: 30 Mayıs 2025
"""

# Import LLM components
from .llm_api_manager import (
    LLMAPIManager, get_llm_api_manager, ProviderType, ModelCapability,
    LLMModel, LLMRequest, LLMResponse
)
from .model_selector import (
    ModelSelector, get_model_selector, SelectionStrategy, TaskComplexity,
    ModelPerformance, TaskRequirements
)

# Version information
__version__ = "8.2.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'LLMAPIManager',
    'ModelSelector',
    'LLMModel',
    'LLMRequest',
    'LLMResponse',
    'ModelPerformance',
    'TaskRequirements',
    
    # Enums
    'ProviderType',
    'ModelCapability',
    'SelectionStrategy',
    'TaskComplexity',
    
    # Functions
    'get_llm_api_manager',
    'get_model_selector',
    
    # Utilities
    'initialize_llm_system',
    'get_llm_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_llm_system() -> bool:
    """
    Initialize the complete LLM management system.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize LLM API Manager
        llm_manager = get_llm_api_manager()
        
        # Initialize Model Selector
        model_selector = get_model_selector()
        
        logger.info("🤖 LLM system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing LLM system: {e}")
        return False

def get_llm_info() -> dict:
    """
    Get LLM module information.
    
    Returns:
        Dictionary containing LLM module information
    """
    return {
        'module': 'orion_vision_core.llm',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'LLMAPIManager': 'Multi-provider LLM API management',
            'ModelSelector': 'Intelligent model selection and optimization'
        },
        'features': [
            'Multi-provider API support',
            'Dynamic model selection',
            'Cost optimization',
            'Performance monitoring',
            'Fallback mechanisms',
            'Usage tracking',
            'API key management',
            'Model capability matching'
        ],
        'supported_providers': [
            'OpenAI (GPT-4, GPT-3.5)',
            'Anthropic (Claude 3)',
            'Local models (Ollama)',
            'HuggingFace models',
            'Custom providers'
        ],
        'selection_strategies': [
            'Cost optimized',
            'Performance optimized',
            'Balanced',
            'Local preferred',
            'Fastest response',
            'Most capable'
        ]
    }

# Module initialization
logger.info(f"📦 Orion Vision Core LLM Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
