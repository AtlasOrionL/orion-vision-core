#!/usr/bin/env python3
"""
Orion Vision Core Brain Module
Sprint 8.2 - Advanced LLM Management and Core "Brain" AI Capabilities
Orion Vision Core - Autonomous AI Operating System

This module provides advanced AI brain capabilities including task analysis,
message fragmentation, and intelligent processing optimization for the
Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.2.0
Date: 30 Mayıs 2025
"""

# Import brain components
from .brain_ai_manager import (
    BrainAIManager, get_brain_ai_manager, TaskType, MessageFragmentType,
    MessageFragment, TaskAnalysis
)

# Version information
__version__ = "8.2.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'BrainAIManager',
    'MessageFragment',
    'TaskAnalysis',
    
    # Enums
    'TaskType',
    'MessageFragmentType',
    
    # Functions
    'get_brain_ai_manager',
    
    # Utilities
    'initialize_brain_system',
    'get_brain_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_brain_system() -> bool:
    """
    Initialize the complete brain AI system.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize Brain AI Manager
        brain_manager = get_brain_ai_manager()
        
        logger.info("🧠 Brain AI system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing brain AI system: {e}")
        return False

def get_brain_info() -> dict:
    """
    Get brain module information.
    
    Returns:
        Dictionary containing brain module information
    """
    return {
        'module': 'orion_vision_core.brain',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'BrainAIManager': 'Advanced AI task optimization and message processing'
        },
        'features': [
            'Intelligent task analysis',
            'Message fragmentation',
            'Task complexity estimation',
            'Optimal model routing',
            'Context management',
            'Learning from execution',
            'Performance optimization',
            'Pattern recognition'
        ],
        'task_types': [
            'Conversation',
            'Analysis',
            'Code generation',
            'Summarization',
            'Translation',
            'Reasoning',
            'Creative writing',
            'Problem solving'
        ],
        'optimization_strategies': [
            'Context compression',
            'Model routing',
            'Message chunking',
            'Parallel processing'
        ]
    }

# Module initialization
logger.info(f"📦 Orion Vision Core Brain Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
