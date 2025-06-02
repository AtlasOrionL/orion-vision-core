#!/usr/bin/env python3
"""
Orion Vision Core - Main Package
Enterprise-grade AI framework with 107 production modules
"""

__version__ = "1.0.0"
__author__ = "Orion Development Team"

# Core exports
from .agent_core import Agent, AgentConfig, AgentStatus, AgentLogger, AgentCore
from .agent_registry import AgentRegistry, get_global_registry
from .dynamic_agent_loader import DynamicAgentLoader
from .task_orchestration import TaskScheduler, TaskDefinition, TaskExecution
from .core_ai_manager import CoreAIManager

__all__ = [
    "Agent",
    "AgentConfig",
    "AgentStatus",
    "AgentLogger",
    "AgentCore",
    "AgentRegistry",
    "get_global_registry",
    "DynamicAgentLoader",
    "TaskScheduler",
    "TaskDefinition",
    "TaskExecution",
    "CoreAIManager"
]