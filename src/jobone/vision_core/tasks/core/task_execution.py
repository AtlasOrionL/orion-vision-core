"""
Task Execution Classes for Orion Vision Core

This module contains task execution state management and tracking.
Extracted from task_orchestration.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .task_base import TaskStatus


@dataclass
class TaskExecution:
    """
    Task Execution State
    
    Tracks task execution state, progress, and results.
    """
    # Core identification
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    assigned_agent: str = ""
    assigned_service_id: str = ""
    
    # Execution state
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    
    # Results
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    error_details: Dict[str, Any] = field(default_factory=dict)
    
    # Progress tracking
    progress_percentage: float = 0.0
    progress_message: str = ""
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    
    # Retry information
    attempt_number: int = 1
    retry_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Performance metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_usage: float = 0.0
    
    def start_execution(self, agent_id: str, service_id: str = ""):
        """Start task execution"""
        self.assigned_agent = agent_id
        self.assigned_service_id = service_id
        self.status = TaskStatus.RUNNING
        self.start_time = time.time()
        self.progress_percentage = 0.0
        self.progress_message = "Task started"
        
        # Add start checkpoint
        self.checkpoints.append({
            'timestamp': self.start_time,
            'percentage': 0.0,
            'message': 'Task execution started',
            'agent_id': agent_id,
            'service_id': service_id
        })
    
    def complete_execution(self, output_data: Dict[str, Any] = None):
        """Complete task execution successfully"""
        self.status = TaskStatus.COMPLETED
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.progress_percentage = 100.0
        self.progress_message = "Task completed successfully"
        if output_data:
            self.output_data = output_data
        
        # Add completion checkpoint
        self.checkpoints.append({
            'timestamp': self.end_time,
            'percentage': 100.0,
            'message': 'Task execution completed',
            'duration': self.duration
        })
    
    def fail_execution(self, error_message: str, error_details: Dict[str, Any] = None):
        """Mark task execution as failed"""
        self.status = TaskStatus.FAILED
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.error_message = error_message
        self.error_details = error_details or {}
        self.progress_message = f"Task failed: {error_message}"
        
        # Add failure checkpoint
        self.checkpoints.append({
            'timestamp': self.end_time,
            'percentage': self.progress_percentage,
            'message': f'Task execution failed: {error_message}',
            'error_details': self.error_details,
            'duration': self.duration
        })
    
    def timeout_execution(self):
        """Mark task execution as timed out"""
        self.status = TaskStatus.TIMEOUT
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.error_message = "Task execution timed out"
        self.progress_message = "Task timed out"
        
        # Add timeout checkpoint
        self.checkpoints.append({
            'timestamp': self.end_time,
            'percentage': self.progress_percentage,
            'message': 'Task execution timed out',
            'duration': self.duration
        })
    
    def cancel_execution(self):
        """Cancel task execution"""
        self.status = TaskStatus.CANCELLED
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.progress_message = "Task cancelled"
        
        # Add cancellation checkpoint
        self.checkpoints.append({
            'timestamp': self.end_time,
            'percentage': self.progress_percentage,
            'message': 'Task execution cancelled',
            'duration': self.duration
        })
    
    def update_progress(self, percentage: float, message: str = ""):
        """Update task execution progress"""
        self.progress_percentage = max(0.0, min(100.0, percentage))
        if message:
            self.progress_message = message
        
        # Add progress checkpoint
        self.checkpoints.append({
            'timestamp': time.time(),
            'percentage': self.progress_percentage,
            'message': self.progress_message
        })
    
    def update_performance_metrics(self, cpu_usage: float = None, 
                                 memory_usage: float = None, 
                                 network_usage: float = None):
        """Update performance metrics"""
        if cpu_usage is not None:
            self.cpu_usage = cpu_usage
        if memory_usage is not None:
            self.memory_usage = memory_usage
        if network_usage is not None:
            self.network_usage = network_usage
        
        # Add performance checkpoint
        self.checkpoints.append({
            'timestamp': time.time(),
            'percentage': self.progress_percentage,
            'message': 'Performance metrics updated',
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'network_usage': self.network_usage
        })
    
    def add_retry_attempt(self, error_message: str):
        """Record retry attempt"""
        self.retry_history.append({
            'attempt': self.attempt_number,
            'timestamp': time.time(),
            'error': error_message,
            'duration': self.duration,
            'progress_reached': self.progress_percentage
        })
        self.attempt_number += 1
        
        # Reset execution state for retry
        self.status = TaskStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.progress_percentage = 0.0
        self.progress_message = f"Retrying (attempt {self.attempt_number})"
        self.error_message = ""
        self.error_details = {}
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        return {
            'execution_id': self.execution_id,
            'task_id': self.task_id,
            'status': self.status.value,
            'assigned_agent': self.assigned_agent,
            'duration': self.duration,
            'progress_percentage': self.progress_percentage,
            'attempt_number': self.attempt_number,
            'total_retries': len(self.retry_history),
            'has_error': bool(self.error_message),
            'checkpoints_count': len(self.checkpoints)
        }
    
    def is_running(self) -> bool:
        """Check if task is currently running"""
        return self.status == TaskStatus.RUNNING
    
    def is_completed(self) -> bool:
        """Check if task completed successfully"""
        return self.status == TaskStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if task failed"""
        return self.status in [TaskStatus.FAILED, TaskStatus.TIMEOUT]
    
    def is_finished(self) -> bool:
        """Check if task execution is finished (completed, failed, or cancelled)"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, 
                              TaskStatus.TIMEOUT, TaskStatus.CANCELLED]
    
    def get_runtime_seconds(self) -> Optional[float]:
        """Get current runtime in seconds"""
        if self.start_time is None:
            return None
        
        end_time = self.end_time or time.time()
        return end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task execution to dictionary"""
        return {
            'execution_id': self.execution_id,
            'task_id': self.task_id,
            'assigned_agent': self.assigned_agent,
            'assigned_service_id': self.assigned_service_id,
            'status': self.status.value,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'output_data': self.output_data,
            'error_message': self.error_message,
            'error_details': self.error_details,
            'progress_percentage': self.progress_percentage,
            'progress_message': self.progress_message,
            'checkpoints': self.checkpoints,
            'attempt_number': self.attempt_number,
            'retry_history': self.retry_history,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'network_usage': self.network_usage
        }
