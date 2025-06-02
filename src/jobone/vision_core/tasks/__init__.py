#!/usr/bin/env python3
"""
Orion Vision Core Tasks Module
Sprint 9.1.1.1 - Core Framework Optimization & Modularization
Orion Vision Core - Autonomous AI Operating System

This module provides comprehensive task execution capabilities including
modular task framework, orchestration, workflow management, and safety
mechanisms for the Orion Vision Core autonomous AI operating system.

Author: Atlas-orion (Augment Agent) & Orion Development Team
Version: 9.1.1.1 (Modularized)
Date: 1 Haziran 2025
"""

# Import legacy task components (for backward compatibility)
try:
    from .task_framework import (
        TaskManager, get_task_manager, TaskType,
        TaskStep, BaseTaskExecutor,
        SystemCommandExecutor, FileOperationExecutor
    )
    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False

# Import new modular components (Sprint 9.1.1.1)
from .core import (
    TaskStatus,
    TaskPriority,
    WorkflowStatus,
    ConsensusType,
    TaskDefinition,
    TaskExecution
)

from .orchestration import (
    TaskScheduler,
    TaskExecutor
)

from .workflow import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowStep,
    WorkflowExecution,
    WorkflowBuilder
)

# Version information
__version__ = "9.1.1.1"
__author__ = "Atlas-orion (Augment Agent) & Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # New modular components (Sprint 9.1.1.1)
    'TaskStatus',
    'TaskPriority',
    'WorkflowStatus',
    'ConsensusType',
    'TaskDefinition',
    'TaskExecution',
    'TaskScheduler',
    'TaskExecutor',
    'WorkflowEngine',
    'WorkflowDefinition',
    'WorkflowStep',
    'WorkflowExecution',
    'WorkflowBuilder',

    # Legacy components (backward compatibility)
    'TaskManager',
    'TaskStep',
    'BaseTaskExecutor',
    'SystemCommandExecutor',
    'FileOperationExecutor',
    'TaskType',
    'get_task_manager',

    # Utilities
    'initialize_task_system',
    'get_task_info',
    'create_simple_task',
    'LEGACY_AVAILABLE'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def initialize_task_system() -> bool:
    """
    Initialize the complete task execution system.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize Task Manager
        task_manager = get_task_manager()
        
        logger.info("🎯 Task system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing task system: {e}")
        return False

def get_task_info() -> dict:
    """
    Get task module information.
    
    Returns:
        Dictionary containing task module information
    """
    return {
        'module': 'orion_vision_core.tasks',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'TaskManager': 'Central task scheduling and execution system',
            'SystemCommandExecutor': 'Safe system command execution',
            'FileOperationExecutor': 'Secure file operation execution'
        },
        'features': [
            'Autonomous task execution',
            'Safety monitoring and enforcement',
            'Progress tracking and reporting',
            'Error handling and recovery',
            'Resource management',
            'Comprehensive logging',
            'Task scheduling and queuing',
            'Concurrent execution management',
            'Timeout and cancellation support'
        ],
        'task_types': [
            'System commands',
            'File operations',
            'Data processing',
            'Analysis tasks',
            'Automation workflows',
            'Monitoring tasks',
            'Custom tasks'
        ],
        'safety_features': [
            'Task validation before execution',
            'Safety level enforcement',
            'Resource usage monitoring',
            'Execution timeout management',
            'Error recovery mechanisms',
            'Comprehensive audit logging'
        ]
    }

def create_simple_task(name: str, description: str, steps: list, 
                      task_type: TaskType = TaskType.AUTOMATION,
                      priority: TaskPriority = TaskPriority.NORMAL) -> str:
    """
    Create a simple task with basic configuration.
    
    Args:
        name: Task name
        description: Task description
        steps: List of task steps
        task_type: Type of task
        priority: Task priority
        
    Returns:
        Task ID if successful, None otherwise
    """
    try:
        task_manager = get_task_manager()
        
        task_id = task_manager.create_task(
            name=name,
            description=description,
            task_type=task_type,
            steps=steps,
            priority=priority
        )
        
        if task_id:
            logger.info(f"🎯 Simple task created: {name} (ID: {task_id})")
        
        return task_id
        
    except Exception as e:
        logger.error(f"❌ Error creating simple task: {e}")
        return None

# Module initialization
logger.info(f"📦 Orion Vision Core Tasks Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
