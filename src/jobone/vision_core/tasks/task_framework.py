#!/usr/bin/env python3
"""
Task Framework - Autonomous Task Execution System
Sprint 8.3 - Basic Computer Management and First Autonomous Task
Orion Vision Core - Autonomous AI Operating System

This module provides a comprehensive framework for autonomous task execution
with safety mechanisms, monitoring, and comprehensive logging for the
Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.3.0
Date: 30 Mayıs 2025
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from ..system.terminal_manager import get_terminal_manager
from ..system.file_system_manager import get_file_system_manager
from ..brain.brain_ai_manager import get_brain_ai_manager
from ..llm.llm_api_manager import get_llm_api_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaskFramework")

class TaskStatus(Enum):
    """Task execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class TaskPriority(Enum):
    """Task priority enumeration"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class TaskType(Enum):
    """Task type enumeration"""
    SYSTEM_COMMAND = "system_command"
    FILE_OPERATION = "file_operation"
    DATA_PROCESSING = "data_processing"
    ANALYSIS = "analysis"
    AUTOMATION = "automation"
    MONITORING = "monitoring"
    CUSTOM = "custom"

@dataclass
class TaskStep:
    """Individual task step"""
    step_id: str
    description: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_result: Optional[str] = None
    timeout: int = 30
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    timestamp: Optional[datetime] = None

@dataclass
class TaskDefinition:
    """Complete task definition"""
    task_id: str
    name: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    steps: List[TaskStep]
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300  # 5 minutes default
    max_retries: int = 3
    safety_level: str = "moderate"
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskExecution:
    """Task execution record"""
    execution_id: str
    task_definition: TaskDefinition
    status: TaskStatus
    current_step: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_execution_time: float
    success_rate: float
    results: List[Any]
    errors: List[str]
    logs: List[str]

class BaseTaskExecutor(ABC):
    """Base class for task executors"""

    @abstractmethod
    async def execute_step(self, step: TaskStep, context: Dict[str, Any]) -> tuple[bool, Any, Optional[str]]:
        """
        Execute a single task step.

        Args:
            step: Task step to execute
            context: Execution context

        Returns:
            Tuple of (success, result, error_message)
        """
        pass

    @abstractmethod
    def validate_step(self, step: TaskStep) -> tuple[bool, Optional[str]]:
        """
        Validate a task step before execution.

        Args:
            step: Task step to validate

        Returns:
            Tuple of (valid, error_message)
        """
        pass

class SystemCommandExecutor(BaseTaskExecutor):
    """Executor for system commands"""

    def __init__(self):
        self.terminal_manager = get_terminal_manager()

    async def execute_step(self, step: TaskStep, context: Dict[str, Any]) -> tuple[bool, Any, Optional[str]]:
        """Execute system command step"""
        try:
            command = step.parameters.get('command')
            working_dir = step.parameters.get('working_dir')
            force_execution = step.parameters.get('force_execution', False)

            if not command:
                return False, None, "No command specified"

            # Execute command
            command_id = self.terminal_manager.execute_command(
                command=command,
                working_dir=working_dir,
                timeout=step.timeout,
                force_execution=force_execution
            )

            if not command_id:
                return False, None, "Command execution blocked or failed to start"

            # Wait for completion (simplified - in real implementation would use proper async waiting)
            await asyncio.sleep(1)  # Placeholder for actual waiting logic

            # Get command history to find our result
            history = self.terminal_manager.get_command_history(limit=10)
            for cmd_result in reversed(history):
                if cmd_result['command_id'] == command_id:
                    if cmd_result['status'] == 'completed':
                        return True, cmd_result, None
                    else:
                        return False, cmd_result, cmd_result.get('stderr', 'Command failed')

            return False, None, "Command result not found"

        except Exception as e:
            return False, None, f"Error executing system command: {e}"

    def validate_step(self, step: TaskStep) -> tuple[bool, Optional[str]]:
        """Validate system command step"""
        command = step.parameters.get('command')
        if not command:
            return False, "No command specified"

        # Additional validation could be added here
        return True, None

class FileOperationExecutor(BaseTaskExecutor):
    """Executor for file operations"""

    def __init__(self):
        self.file_manager = get_file_system_manager()

    async def execute_step(self, step: TaskStep, context: Dict[str, Any]) -> tuple[bool, Any, Optional[str]]:
        """Execute file operation step"""
        try:
            operation = step.parameters.get('operation')

            if operation == 'read':
                file_path = step.parameters.get('file_path')
                encoding = step.parameters.get('encoding', 'utf-8')

                content = self.file_manager.read_file(file_path, encoding)
                if content is not None:
                    return True, content, None
                else:
                    return False, None, f"Failed to read file: {file_path}"

            elif operation == 'write':
                file_path = step.parameters.get('file_path')
                content = step.parameters.get('content', '')
                encoding = step.parameters.get('encoding', 'utf-8')

                success = self.file_manager.write_file(file_path, content, encoding)
                if success:
                    return True, f"File written: {file_path}", None
                else:
                    return False, None, f"Failed to write file: {file_path}"

            elif operation == 'copy':
                source_path = step.parameters.get('source_path')
                target_path = step.parameters.get('target_path')

                success = self.file_manager.copy_file(source_path, target_path)
                if success:
                    return True, f"File copied: {source_path} → {target_path}", None
                else:
                    return False, None, f"Failed to copy file: {source_path} → {target_path}"

            elif operation == 'delete':
                file_path = step.parameters.get('file_path')
                force = step.parameters.get('force', False)

                success = self.file_manager.delete_file(file_path, force)
                if success:
                    return True, f"File deleted: {file_path}", None
                else:
                    return False, None, f"Failed to delete file: {file_path}"

            elif operation == 'list':
                directory_path = step.parameters.get('directory_path')
                include_hidden = step.parameters.get('include_hidden', False)

                items = self.file_manager.list_directory(directory_path, include_hidden)
                if items is not None:
                    return True, items, None
                else:
                    return False, None, f"Failed to list directory: {directory_path}"

            else:
                return False, None, f"Unknown file operation: {operation}"

        except Exception as e:
            return False, None, f"Error executing file operation: {e}"

    def validate_step(self, step: TaskStep) -> tuple[bool, Optional[str]]:
        """Validate file operation step"""
        operation = step.parameters.get('operation')
        if not operation:
            return False, "No operation specified"

        valid_operations = ['read', 'write', 'copy', 'delete', 'list']
        if operation not in valid_operations:
            return False, f"Invalid operation: {operation}"

        # Operation-specific validation
        if operation in ['read', 'write', 'delete']:
            if not step.parameters.get('file_path'):
                return False, f"No file_path specified for {operation} operation"

        elif operation == 'copy':
            if not step.parameters.get('source_path') or not step.parameters.get('target_path'):
                return False, "source_path and target_path required for copy operation"

        elif operation == 'list':
            if not step.parameters.get('directory_path'):
                return False, "No directory_path specified for list operation"

        return True, None

class TaskManager(QObject):
    """
    Central task management system.

    Features:
    - Task scheduling and execution
    - Safety monitoring and enforcement
    - Progress tracking and reporting
    - Error handling and recovery
    - Resource management
    - Comprehensive logging
    """

    # Signals
    task_started = pyqtSignal(str)  # task_id
    task_completed = pyqtSignal(str, dict)  # task_id, results
    task_failed = pyqtSignal(str, str)  # task_id, error
    task_progress = pyqtSignal(str, int, int)  # task_id, current_step, total_steps
    safety_violation = pyqtSignal(str, str)  # task_id, violation_type

    def __init__(self):
        """Initialize Task Manager"""
        super().__init__()

        # Component references
        self.terminal_manager = get_terminal_manager()
        self.file_manager = get_file_system_manager()
        self.brain_manager = get_brain_ai_manager()
        self.llm_manager = get_llm_api_manager()

        # Executors
        self.executors = {
            'system_command': SystemCommandExecutor(),
            'file_operation': FileOperationExecutor(),
        }

        # Task management
        self.active_tasks: Dict[str, TaskExecution] = {}
        self.task_queue: List[TaskDefinition] = []
        self.task_history: List[TaskExecution] = []
        self.task_counter = 0

        # Configuration
        self.max_concurrent_tasks = 3
        self.max_task_history = 1000
        self.safety_enabled = True

        # Statistics
        self.execution_stats = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'cancelled_tasks': 0,
            'average_execution_time': 0.0,
            'tasks_by_type': {task_type.value: 0 for task_type in TaskType},
            'tasks_by_priority': {priority.name: 0 for priority in TaskPriority}
        }

        # Monitoring
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self._monitor_tasks)
        self.monitoring_timer.start(1000)  # Monitor every second

        logger.info("🎯 Task Manager initialized")

    def create_task(self, name: str, description: str, task_type: TaskType,
                   steps: List[Dict[str, Any]], priority: TaskPriority = TaskPriority.NORMAL,
                   timeout: int = 300, safety_level: str = "moderate") -> str:
        """
        Create a new task definition.

        Args:
            name: Task name
            description: Task description
            task_type: Type of task
            steps: List of task steps
            priority: Task priority
            timeout: Task timeout in seconds
            safety_level: Safety level (safe, moderate, dangerous)

        Returns:
            Task ID
        """
        try:
            task_id = self._generate_task_id()

            # Create task steps
            task_steps = []
            for i, step_data in enumerate(steps):
                step = TaskStep(
                    step_id=f"{task_id}_step_{i+1:02d}",
                    description=step_data.get('description', f'Step {i+1}'),
                    action=step_data.get('action', ''),
                    parameters=step_data.get('parameters', {}),
                    expected_result=step_data.get('expected_result'),
                    timeout=step_data.get('timeout', 30),
                    max_retries=step_data.get('max_retries', 3)
                )
                task_steps.append(step)

            # Create task definition
            task_definition = TaskDefinition(
                task_id=task_id,
                name=name,
                description=description,
                task_type=task_type,
                priority=priority,
                steps=task_steps,
                timeout=timeout,
                safety_level=safety_level,
                created_by="user",
                metadata={'created_at': datetime.now().isoformat()}
            )

            # Validate task
            if not self._validate_task(task_definition):
                logger.error(f"❌ Task validation failed: {task_id}")
                return None

            # Add to queue
            self.task_queue.append(task_definition)
            self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)

            logger.info(f"🎯 Created task: {name} (ID: {task_id})")
            return task_id

        except Exception as e:
            logger.error(f"❌ Error creating task: {e}")
            return None

    def get_task_queue(self) -> List[Dict[str, Any]]:
        """Get current task queue"""
        return [self._task_definition_to_dict(task) for task in self.task_queue]

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get currently active tasks"""
        return [self._task_execution_to_dict(execution) for execution in self.active_tasks.values()]

    def get_task_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get task execution history"""
        history = self.task_history[-limit:] if limit > 0 else self.task_history
        return [self._task_execution_to_dict(execution) for execution in history]

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.execution_stats.copy()

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        try:
            # Cancel active task
            if task_id in self.active_tasks:
                execution = self.active_tasks[task_id]
                execution.status = TaskStatus.CANCELLED
                execution.errors.append("Task cancelled by user")
                self._complete_task(execution, False)
                self.execution_stats['cancelled_tasks'] += 1
                logger.info(f"🎯 Task cancelled: {task_id}")
                return True

            # Remove from queue
            for task in self.task_queue:
                if task.task_id == task_id:
                    self.task_queue.remove(task)
                    logger.info(f"🎯 Task removed from queue: {task_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ Error cancelling task: {e}")
            return False

    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        self.task_counter += 1
        return f"task_{self.task_counter:06d}"

    def _task_definition_to_dict(self, task: TaskDefinition) -> Dict[str, Any]:
        """Convert TaskDefinition to dictionary"""
        return {
            'task_id': task.task_id,
            'name': task.name,
            'description': task.description,
            'task_type': task.task_type.value,
            'priority': task.priority.name,
            'steps_count': len(task.steps),
            'timeout': task.timeout,
            'safety_level': task.safety_level,
            'created_by': task.created_by,
            'metadata': task.metadata
        }

    def _task_execution_to_dict(self, execution: TaskExecution) -> Dict[str, Any]:
        """Convert TaskExecution to dictionary"""
        return {
            'execution_id': execution.execution_id,
            'task_id': execution.task_definition.task_id,
            'task_name': execution.task_definition.name,
            'status': execution.status.value,
            'current_step': execution.current_step,
            'total_steps': len(execution.task_definition.steps),
            'start_time': execution.start_time.isoformat() if execution.start_time else None,
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'execution_time': execution.total_execution_time,
            'success_rate': execution.success_rate,
            'results_count': len(execution.results),
            'errors_count': len(execution.errors)
        }

    def _validate_task(self, task_definition: TaskDefinition) -> bool:
        """Validate task definition"""
        try:
            # Basic validation
            if not task_definition.name or not task_definition.steps:
                return False

            # Safety validation
            if self.safety_enabled and task_definition.safety_level == "dangerous":
                logger.warning(f"⚠️ Dangerous task blocked: {task_definition.task_id}")
                self.safety_violation.emit(task_definition.task_id, "dangerous_task")
                return False

            # Validate each step
            for step in task_definition.steps:
                executor = self._get_executor(step.action)
                if not executor:
                    logger.error(f"❌ No executor for action: {step.action}")
                    return False

                valid, error = executor.validate_step(step)
                if not valid:
                    logger.error(f"❌ Step validation failed: {error}")
                    return False

            return True

        except Exception as e:
            logger.error(f"❌ Error validating task: {e}")
            return False

    def _get_executor(self, action: str) -> Optional[BaseTaskExecutor]:
        """Get appropriate executor for action"""
        return self.executors.get(action)

    def _complete_task(self, execution: TaskExecution, success: bool):
        """Complete task execution"""
        try:
            execution.end_time = datetime.now()
            execution.total_execution_time = (execution.end_time - execution.start_time).total_seconds()

            if success:
                execution.status = TaskStatus.COMPLETED
                self.execution_stats['successful_tasks'] += 1
                self.task_completed.emit(execution.task_definition.task_id, {
                    'results': execution.results,
                    'execution_time': execution.total_execution_time,
                    'success_rate': execution.success_rate
                })
            else:
                execution.status = TaskStatus.FAILED
                self.execution_stats['failed_tasks'] += 1
                self.task_failed.emit(execution.task_definition.task_id,
                                    '; '.join(execution.errors) if execution.errors else 'Unknown error')

            # Update statistics
            self.execution_stats['total_tasks'] += 1
            self.execution_stats['tasks_by_type'][execution.task_definition.task_type.value] += 1
            self.execution_stats['tasks_by_priority'][execution.task_definition.priority.name] += 1

            # Move to history
            self.task_history.append(execution)
            if len(self.task_history) > self.max_task_history:
                self.task_history.pop(0)

            # Remove from active tasks
            if execution.task_definition.task_id in self.active_tasks:
                del self.active_tasks[execution.task_definition.task_id]

            logger.info(f"🎯 Task completed: {execution.task_definition.task_id} "
                       f"(Status: {execution.status.value}, Time: {execution.total_execution_time:.2f}s)")

        except Exception as e:
            logger.error(f"❌ Error completing task: {e}")

    def _monitor_tasks(self):
        """Monitor active tasks for timeouts and issues"""
        try:
            current_time = datetime.now()

            for task_id, execution in list(self.active_tasks.items()):
                # Check for timeout
                if execution.start_time:
                    elapsed_time = (current_time - execution.start_time).total_seconds()
                    if elapsed_time > execution.task_definition.timeout:
                        logger.warning(f"⚠️ Task timeout: {task_id}")
                        execution.status = TaskStatus.TIMEOUT
                        execution.errors.append("Task timeout")
                        self._complete_task(execution, False)

        except Exception as e:
            logger.error(f"❌ Error monitoring tasks: {e}")

# Singleton instance
_task_manager = None

def get_task_manager() -> TaskManager:
    """Get the singleton Task Manager instance"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager