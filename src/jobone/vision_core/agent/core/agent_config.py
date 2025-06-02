"""
Agent Configuration Classes for Orion Vision Core

This module contains configuration classes and utilities for agents.
Extracted from agent_core.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from .agent_status import AgentPriority


@dataclass
class AgentConfig:
    """Configuration class for agent initialization and runtime settings"""
    
    # Core identification
    agent_id: str
    agent_name: str
    agent_type: str
    
    # Runtime settings
    priority: AgentPriority = AgentPriority.NORMAL
    log_level: str = "INFO"
    heartbeat_interval: float = 5.0
    max_retries: int = 3
    timeout: float = 30.0
    auto_restart: bool = True
    
    # Advanced configuration
    config_data: Optional[Dict[str, Any]] = field(default_factory=dict)
    environment_vars: Optional[Dict[str, str]] = field(default_factory=dict)
    dependencies: Optional[List[str]] = field(default_factory=list)
    
    # Resource limits
    max_memory_mb: Optional[int] = None
    max_cpu_percent: Optional[float] = None
    max_threads: Optional[int] = None
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.agent_id:
            raise ValueError("agent_id cannot be empty")
        if not self.agent_name:
            raise ValueError("agent_name cannot be empty")
        if not self.agent_type:
            raise ValueError("agent_type cannot be empty")
        if self.heartbeat_interval <= 0:
            raise ValueError("heartbeat_interval must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'priority': self.priority.value,
            'log_level': self.log_level,
            'heartbeat_interval': self.heartbeat_interval,
            'max_retries': self.max_retries,
            'timeout': self.timeout,
            'auto_restart': self.auto_restart,
            'config_data': self.config_data,
            'environment_vars': self.environment_vars,
            'dependencies': self.dependencies,
            'max_memory_mb': self.max_memory_mb,
            'max_cpu_percent': self.max_cpu_percent,
            'max_threads': self.max_threads
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Create configuration from dictionary"""
        # Convert priority back to enum
        if 'priority' in data and isinstance(data['priority'], int):
            data['priority'] = AgentPriority(data['priority'])
        
        return cls(**data)
    
    def validate(self) -> bool:
        """Validate current configuration"""
        try:
            self.__post_init__()
            return True
        except ValueError:
            return False
