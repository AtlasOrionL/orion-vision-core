#!/usr/bin/env python3
"""
Orion Vision Core Workflows Module
Sprint 8.4 - Advanced Task Automation and AI-Driven Workflows
Orion Vision Core - Autonomous AI Operating System

This module provides advanced workflow automation capabilities including
complex task orchestration, dependency management, and intelligent
execution planning for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.4.0
Date: 30 Mayıs 2025
"""

# Import workflow components
from .workflow_engine import (
    WorkflowEngine, get_workflow_engine, WorkflowStatus, DependencyType,
    OptimizationStrategy, WorkflowNode, WorkflowDefinition, WorkflowExecution
)

# Version information
__version__ = "8.4.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'WorkflowEngine',
    'WorkflowNode',
    'WorkflowDefinition',
    'WorkflowExecution',
    
    # Enums
    'WorkflowStatus',
    'DependencyType',
    'OptimizationStrategy',
    
    # Functions
    'get_workflow_engine',
    
    # Utilities
    'initialize_workflow_system',
    'get_workflow_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_workflow_system() -> bool:
    """
    Initialize the complete workflow automation system.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize Workflow Engine
        workflow_engine = get_workflow_engine()
        
        logger.info("🔄 Workflow system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing workflow system: {e}")
        return False

def get_workflow_info() -> dict:
    """
    Get workflow module information.
    
    Returns:
        Dictionary containing workflow module information
    """
    return {
        'module': 'orion_vision_core.workflows',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'WorkflowEngine': 'Advanced workflow automation and orchestration engine'
        },
        'features': [
            'Complex task orchestration',
            'Dependency management',
            'AI-driven workflow optimization',
            'Intelligent execution planning',
            'Dynamic resource allocation',
            'Error recovery and adaptation',
            'Performance monitoring and learning',
            'Multi-objective optimization',
            'Real-time workflow monitoring',
            'Comprehensive audit logging'
        ],
        'optimization_strategies': [
            'Time optimal (minimize execution time)',
            'Resource optimal (minimize resource conflicts)',
            'Cost optimal (minimize execution costs)',
            'Reliability optimal (maximize success probability)',
            'Balanced (optimize multiple objectives)'
        ],
        'dependency_types': [
            'Sequential (task B starts after task A completes)',
            'Parallel (tasks can run simultaneously)',
            'Conditional (task B starts if task A meets condition)',
            'Data flow (task B uses output from task A)'
        ],
        'workflow_capabilities': [
            'Multi-phase execution planning',
            'Parallel task execution',
            'Conditional task execution',
            'Resource-aware scheduling',
            'Failure handling and recovery',
            'Performance optimization',
            'Learning from execution history'
        ]
    }

# Module initialization
logger.info(f"📦 Orion Vision Core Workflows Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
