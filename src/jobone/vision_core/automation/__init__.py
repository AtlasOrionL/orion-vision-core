#!/usr/bin/env python3
"""
Orion Vision Core Automation Module
Sprint 8.4 - Advanced Task Automation and AI-Driven Workflows
Orion Vision Core - Autonomous AI Operating System

This module provides advanced automation capabilities including AI-driven
optimization, intelligent automation orchestration, and adaptive automation
for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.4.0
Date: 30 Mayıs 2025
"""

# Import automation components
from .ai_optimizer import (
    AIOptimizer, get_ai_optimizer, OptimizationType, LearningMode,
    OptimizationResult, PerformanceMetrics
)
from .automation_controller import (
    AutomationController, get_automation_controller, AutomationMode,
    ScheduleType, ResourceType, AutomationRule, AutomationExecution
)

# Version information
__version__ = "8.4.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'AIOptimizer',
    'AutomationController',
    'OptimizationResult',
    'PerformanceMetrics',
    'AutomationRule',
    'AutomationExecution',
    
    # Enums
    'OptimizationType',
    'LearningMode',
    'AutomationMode',
    'ScheduleType',
    'ResourceType',
    
    # Functions
    'get_ai_optimizer',
    'get_automation_controller',
    
    # Utilities
    'initialize_automation_system',
    'get_automation_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_automation_system() -> bool:
    """
    Initialize the complete automation system.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize AI Optimizer
        ai_optimizer = get_ai_optimizer()
        
        # Initialize Automation Controller
        automation_controller = get_automation_controller()
        
        logger.info("🤖 Automation system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing automation system: {e}")
        return False

def get_automation_info() -> dict:
    """
    Get automation module information.
    
    Returns:
        Dictionary containing automation module information
    """
    return {
        'module': 'orion_vision_core.automation',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'AIOptimizer': 'AI-driven optimization for tasks and workflows',
            'AutomationController': 'Advanced automation orchestration and management'
        },
        'features': [
            'AI-driven performance optimization',
            'Intelligent automation scheduling',
            'Resource-aware execution',
            'Adaptive automation strategies',
            'Event-driven automation',
            'Machine learning-based predictions',
            'Real-time optimization recommendations',
            'Continuous learning and improvement',
            'Multi-objective optimization',
            'Comprehensive performance monitoring'
        ],
        'optimization_types': [
            'Performance optimization',
            'Cost optimization',
            'Reliability optimization',
            'Resource usage optimization',
            'Time to completion optimization',
            'Success rate optimization'
        ],
        'automation_modes': [
            'Manual (user-triggered)',
            'Semi-automatic (user approval required)',
            'Fully automatic (autonomous execution)',
            'Adaptive (learns and adapts behavior)'
        ],
        'learning_modes': [
            'Supervised learning',
            'Reinforcement learning',
            'Unsupervised learning',
            'Hybrid learning'
        ],
        'automation_capabilities': [
            'Rule-based automation',
            'Event-driven triggers',
            'Scheduled execution',
            'Resource management',
            'Performance optimization',
            'Error handling and recovery',
            'Comprehensive monitoring and logging'
        ]
    }

# Module initialization
logger.info(f"📦 Orion Vision Core Automation Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
