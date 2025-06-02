"""
Task Base Classes for Orion Vision Core

This module contains core task definitions and base classes.
Extracted from task_orchestration.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    """Task execution status enumeration"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(Enum):
    """Task priority levels for scheduling"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


class WorkflowStatus(Enum):
    """Workflow execution status enumeration"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConsensusType(Enum):
    """Consensus algorithm types for distributed decisions"""
    MAJORITY = "majority"
    UNANIMOUS = "unanimous"
    WEIGHTED = "weighted"
    RAFT = "raft"
    PBFT = "pbft"


@dataclass
class TaskDefinition:
    """
    Task Definition Structure
    
    Comprehensive task definition for distributed task execution.
    """
    # Core identification
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_name: str = ""
    task_type: str = "generic"
    description: str = ""
    
    # Execution requirements
    required_capabilities: List[str] = field(default_factory=list)
    preferred_agents: List[str] = field(default_factory=list)
    excluded_agents: List[str] = field(default_factory=list)
    
    # Task parameters
    input_data: Dict[str, Any] = field(default_factory=dict)
    expected_output: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 300.0  # 5 minutes default
    retry_count: int = 3
    
    # Priority and scheduling
    priority: TaskPriority = TaskPriority.NORMAL
    scheduled_time: Optional[float] = None
    deadline: Optional[float] = None
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    dependent_tasks: List[str] = field(default_factory=list)  # Task IDs
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_time: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validate task definition after initialization"""
        if not self.task_name:
            raise ValueError("task_name cannot be empty")
        if not self.task_type:
            raise ValueError("task_type cannot be empty")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.retry_count < 0:
            raise ValueError("retry_count cannot be negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task definition to dictionary"""
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'task_type': self.task_type,
            'description': self.description,
            'required_capabilities': self.required_capabilities,
            'preferred_agents': self.preferred_agents,
            'excluded_agents': self.excluded_agents,
            'input_data': self.input_data,
            'expected_output': self.expected_output,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'priority': self.priority.value,
            'scheduled_time': self.scheduled_time,
            'deadline': self.deadline,
            'dependencies': self.dependencies,
            'dependent_tasks': self.dependent_tasks,
            'metadata': self.metadata,
            'tags': self.tags,
            'created_time': self.created_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskDefinition':
        """Create task definition from dictionary"""
        # Convert priority back to enum
        priority_value = data.get('priority', TaskPriority.NORMAL.value)
        if isinstance(priority_value, int):
            priority = TaskPriority(priority_value)
        else:
            priority = TaskPriority.NORMAL
        
        return cls(
            task_id=data.get('task_id', str(uuid.uuid4())),
            task_name=data.get('task_name', ''),
            task_type=data.get('task_type', 'generic'),
            description=data.get('description', ''),
            required_capabilities=data.get('required_capabilities', []),
            preferred_agents=data.get('preferred_agents', []),
            excluded_agents=data.get('excluded_agents', []),
            input_data=data.get('input_data', {}),
            expected_output=data.get('expected_output', {}),
            timeout=data.get('timeout', 300.0),
            retry_count=data.get('retry_count', 3),
            priority=priority,
            scheduled_time=data.get('scheduled_time'),
            deadline=data.get('deadline'),
            dependencies=data.get('dependencies', []),
            dependent_tasks=data.get('dependent_tasks', []),
            metadata=data.get('metadata', {}),
            tags=data.get('tags', []),
            created_time=data.get('created_time', time.time())
        )
    
    def validate(self) -> bool:
        """Validate current task definition"""
        try:
            self.__post_init__()
            return True
        except ValueError:
            return False
    
    def is_expired(self) -> bool:
        """Check if task has exceeded its deadline"""
        if self.deadline is None:
            return False
        return time.time() > self.deadline
    
    def is_ready_to_run(self) -> bool:
        """Check if task is ready to run (scheduled time passed)"""
        if self.scheduled_time is None:
            return True
        return time.time() >= self.scheduled_time
    
    def get_age_seconds(self) -> float:
        """Get task age in seconds since creation"""
        return time.time() - self.created_time
    
    def add_dependency(self, task_id: str):
        """Add a dependency task"""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
    
    def remove_dependency(self, task_id: str):
        """Remove a dependency task"""
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)
    
    def add_tag(self, tag: str):
        """Add a tag to the task"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag from the task"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if task has a specific tag"""
        return tag in self.tags
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata value"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)


class TaskBase:
    """
    Base Task Class for Orion Vision Core

    Provides the foundation for all task implementations with
    standardized lifecycle management and execution patterns.
    """

    def __init__(self, task_definition: TaskDefinition):
        """Initialize task with definition"""
        self.definition = task_definition
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.execution_context = {}

    def execute(self) -> bool:
        """Execute the task (to be overridden by subclasses)"""
        try:
            self.start_time = time.time()
            self.status = TaskStatus.RUNNING

            # Default implementation - override in subclasses
            result = self._perform_task()

            self.result = result
            self.status = TaskStatus.COMPLETED
            self.end_time = time.time()

            return True

        except Exception as e:
            self.error = str(e)
            self.status = TaskStatus.FAILED
            self.end_time = time.time()
            return False

    def _perform_task(self) -> Any:
        """Perform the actual task work (override in subclasses)"""
        # Default implementation
        return {"message": "Task completed", "task_id": self.definition.task_id}

    def get_status(self) -> TaskStatus:
        """Get current task status"""
        return self.status

    def get_result(self) -> Any:
        """Get task result"""
        return self.result

    def get_error(self) -> Optional[str]:
        """Get task error if any"""
        return self.error

    def get_execution_time(self) -> Optional[float]:
        """Get task execution time in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def cancel(self) -> bool:
        """Cancel the task"""
        if self.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED]:
            self.status = TaskStatus.CANCELLED
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'definition': self.definition.to_dict(),
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'execution_time': self.get_execution_time(),
            'execution_context': self.execution_context
        }
