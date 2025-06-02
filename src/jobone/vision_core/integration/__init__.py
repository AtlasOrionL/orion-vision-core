"""
Integration Module Exports

This module exports all integration classes and utilities.
Part of Sprint 9.9 Advanced Integration & Deployment development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

# Core integration classes
from .core import (
    IntegrationManager,
    IntegrationConfig,
    IntegrationMetrics,
    IntegrationEvent,
    IntegrationType,
    IntegrationStatus,
    ConnectionProtocol
)

# Deployment classes
from .deployment import (
    DeploymentManager,
    DeploymentConfig,
    DeploymentResult,
    EnvironmentInfo,
    DeploymentEnvironment,
    DeploymentStrategy,
    DeploymentStatus,
    DeploymentTarget
)

# Orchestration classes
from .orchestration import (
    OrchestrationManager,
    OrchestrationTask,
    WorkflowDefinition,
    WorkflowExecution,
    OrchestrationMode,
    WorkflowStatus,
    TaskType
)

__all__ = [
    # Core Integration
    'IntegrationManager',
    'IntegrationConfig',
    'IntegrationMetrics',
    'IntegrationEvent',
    'IntegrationType',
    'IntegrationStatus',
    'ConnectionProtocol',
    
    # Deployment
    'DeploymentManager',
    'DeploymentConfig',
    'DeploymentResult',
    'EnvironmentInfo',
    'DeploymentEnvironment',
    'DeploymentStrategy',
    'DeploymentStatus',
    'DeploymentTarget',
    
    # Orchestration
    'OrchestrationManager',
    'OrchestrationTask',
    'WorkflowDefinition',
    'WorkflowExecution',
    'OrchestrationMode',
    'WorkflowStatus',
    'TaskType'
]

__version__ = "9.9.0"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.9 - Advanced Integration & Deployment"
