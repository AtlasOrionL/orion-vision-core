"""
Agent Status and Priority Enums for Orion Vision Core

This module contains the core status and priority definitions for agents.
Extracted from agent_core.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

from enum import Enum
from typing import Optional


class AgentStatus(Enum):
    """Agent lifecycle status enumeration"""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    PAUSED = "paused"


class AgentPriority(Enum):
    """Agent priority levels for task scheduling"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


def get_status_description(status: AgentStatus) -> str:
    """Get human-readable description of agent status"""
    descriptions = {
        AgentStatus.IDLE: "Agent is idle and ready for tasks",
        AgentStatus.STARTING: "Agent is starting up",
        AgentStatus.RUNNING: "Agent is actively running",
        AgentStatus.STOPPING: "Agent is shutting down",
        AgentStatus.STOPPED: "Agent has stopped",
        AgentStatus.ERROR: "Agent encountered an error",
        AgentStatus.PAUSED: "Agent is paused"
    }
    return descriptions.get(status, "Unknown status")


def get_priority_description(priority: AgentPriority) -> str:
    """Get human-readable description of agent priority"""
    descriptions = {
        AgentPriority.LOW: "Low priority tasks",
        AgentPriority.NORMAL: "Normal priority tasks",
        AgentPriority.HIGH: "High priority tasks",
        AgentPriority.CRITICAL: "Critical priority tasks",
        AgentPriority.EMERGENCY: "Emergency priority tasks"
    }
    return descriptions.get(priority, "Unknown priority")
