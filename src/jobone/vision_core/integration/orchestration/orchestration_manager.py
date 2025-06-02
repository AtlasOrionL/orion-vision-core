"""
Orchestration Manager for Orion Vision Core

This module provides comprehensive orchestration management including
workflow orchestration, service coordination, and system automation.
Part of Sprint 9.9 Advanced Integration & Deployment development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.9 - Advanced Integration & Deployment
"""

import time
import threading
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class OrchestrationMode(Enum):
    """Orchestration mode enumeration"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    EVENT_DRIVEN = "event_driven"
    SCHEDULED = "scheduled"
    REACTIVE = "reactive"


class WorkflowStatus(Enum):
    """Workflow status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskType(Enum):
    """Task type enumeration"""
    DEPLOYMENT = "deployment"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    BACKUP = "backup"
    SCALING = "scaling"
    MAINTENANCE = "maintenance"
    TESTING = "testing"
    NOTIFICATION = "notification"


@dataclass
class OrchestrationTask:
    """Orchestration task data structure"""
    task_id: str
    task_name: str
    task_type: TaskType
    command: str
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_seconds: float = 5.0
    environment_variables: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    def validate(self) -> bool:
        """Validate task configuration"""
        if not self.task_name or not self.task_id:
            return False
        if not self.command:
            return False
        if self.timeout_seconds <= 0 or self.retry_attempts < 0:
            return False
        return True


@dataclass
class WorkflowDefinition:
    """Workflow definition data structure"""
    workflow_id: str
    workflow_name: str
    description: str
    mode: OrchestrationMode
    tasks: List[OrchestrationTask] = field(default_factory=list)
    schedule: Optional[str] = None  # Cron expression
    triggers: List[str] = field(default_factory=list)
    timeout_minutes: int = 60
    max_concurrent_executions: int = 1
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate workflow definition"""
        if not self.workflow_name or not self.workflow_id:
            return False
        if not self.tasks:
            return False
        if self.timeout_minutes <= 0:
            return False
        
        # Validate all tasks
        for task in self.tasks:
            if not task.validate():
                return False
        
        return True


@dataclass
class WorkflowExecution:
    """Workflow execution data structure"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    start_time: float
    end_time: Optional[float] = None
    current_task_index: int = 0
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    task_results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def get_duration(self) -> float:
        """Get execution duration"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def get_progress_percentage(self, total_tasks: int) -> float:
        """Get execution progress percentage"""
        if total_tasks == 0:
            return 100.0
        return (len(self.completed_tasks) / total_tasks) * 100


class OrchestrationManager:
    """
    Comprehensive orchestration management system
    
    Provides workflow orchestration, service coordination, system automation,
    and execution monitoring with dependency management.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize orchestration manager"""
        self.logger = logger or AgentLogger("orchestration_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Workflow management
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.workflow_executions: Dict[str, WorkflowExecution] = {}
        self.active_executions: Dict[str, threading.Thread] = {}
        
        # Task management
        self.task_registry: Dict[str, Callable] = {}
        
        # Scheduling
        self.scheduler_active = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # Configuration
        self.max_concurrent_workflows = 5
        self.execution_history_limit = 200
        self.task_timeout_default = 300
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.orchestration_stats = {
            'total_workflows': 0,
            'active_workflows': 0,
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_tasks_executed': 0,
            'average_execution_time_minutes': 0.0,
            'scheduler_uptime_hours': 0.0
        }
        
        # Initialize built-in tasks
        self._initialize_builtin_tasks()
        
        self.logger.info("Orchestration Manager initialized")
    
    def _initialize_builtin_tasks(self):
        """Initialize built-in task handlers"""
        self.task_registry['deployment'] = self._execute_deployment_task
        self.task_registry['integration'] = self._execute_integration_task
        self.task_registry['monitoring'] = self._execute_monitoring_task
        self.task_registry['backup'] = self._execute_backup_task
        self.task_registry['scaling'] = self._execute_scaling_task
        self.task_registry['maintenance'] = self._execute_maintenance_task
        self.task_registry['testing'] = self._execute_testing_task
        self.task_registry['notification'] = self._execute_notification_task
    
    def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Register workflow definition"""
        try:
            # Validate workflow
            if not workflow.validate():
                self.logger.error("Invalid workflow definition", workflow_id=workflow.workflow_id)
                return False
            
            with self._lock:
                # Check if workflow already exists
                if workflow.workflow_id in self.workflow_definitions:
                    self.logger.warning("Workflow already exists", workflow_id=workflow.workflow_id)
                    return False
                
                # Register workflow
                self.workflow_definitions[workflow.workflow_id] = workflow
                self.orchestration_stats['total_workflows'] += 1
            
            self.logger.info(
                "Workflow registered",
                workflow_id=workflow.workflow_id,
                workflow_name=workflow.workflow_name,
                mode=workflow.mode.value,
                tasks_count=len(workflow.tasks)
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Workflow registration failed", workflow_id=workflow.workflow_id, error=str(e))
            return False
    
    def execute_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Execute workflow"""
        try:
            if workflow_id not in self.workflow_definitions:
                self.logger.error("Workflow not found", workflow_id=workflow_id)
                return None
            
            workflow = self.workflow_definitions[workflow_id]
            
            # Check if workflow is enabled
            if not workflow.enabled:
                self.logger.error("Workflow is disabled", workflow_id=workflow_id)
                return None
            
            # Check concurrent execution limit
            active_count = len([e for e in self.workflow_executions.values() 
                              if e.workflow_id == workflow_id and e.status == WorkflowStatus.RUNNING])
            
            if active_count >= workflow.max_concurrent_executions:
                self.logger.error("Maximum concurrent executions reached", workflow_id=workflow_id)
                return None
            
            # Create execution
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                start_time=time.time()
            )
            
            with self._lock:
                self.workflow_executions[execution_id] = execution
                self.orchestration_stats['total_executions'] += 1
                self.orchestration_stats['active_workflows'] += 1
            
            # Start execution thread
            execution_thread = threading.Thread(
                target=self._execute_workflow_thread,
                args=(workflow, execution, parameters or {}),
                name=f"Workflow-{execution_id[:8]}",
                daemon=True
            )
            execution_thread.start()
            
            self.active_executions[execution_id] = execution_thread
            
            self.logger.info(
                "Workflow execution started",
                workflow_id=workflow_id,
                execution_id=execution_id,
                workflow_name=workflow.workflow_name
            )
            
            return execution_id
            
        except Exception as e:
            self.logger.error("Workflow execution failed", workflow_id=workflow_id, error=str(e))
            return None
    
    def _execute_workflow_thread(self, workflow: WorkflowDefinition, execution: WorkflowExecution, 
                                parameters: Dict[str, Any]):
        """Execute workflow in thread"""
        try:
            execution.status = WorkflowStatus.RUNNING
            
            self.logger.info(
                "Workflow execution thread started",
                workflow_id=workflow.workflow_id,
                execution_id=execution.execution_id,
                mode=workflow.mode.value
            )
            
            # Execute based on orchestration mode
            if workflow.mode == OrchestrationMode.SEQUENTIAL:
                success = self._execute_sequential(workflow, execution, parameters)
            elif workflow.mode == OrchestrationMode.PARALLEL:
                success = self._execute_parallel(workflow, execution, parameters)
            elif workflow.mode == OrchestrationMode.CONDITIONAL:
                success = self._execute_conditional(workflow, execution, parameters)
            else:
                success = self._execute_sequential(workflow, execution, parameters)  # Default
            
            # Complete execution
            if success:
                self._complete_workflow_execution(workflow, execution)
            else:
                self._fail_workflow_execution(workflow, execution, "Workflow execution failed")
                
        except Exception as e:
            self._fail_workflow_execution(workflow, execution, f"Workflow error: {str(e)}")
    
    def _execute_sequential(self, workflow: WorkflowDefinition, execution: WorkflowExecution, 
                           parameters: Dict[str, Any]) -> bool:
        """Execute workflow sequentially"""
        try:
            for i, task in enumerate(workflow.tasks):
                if not task.enabled:
                    continue
                
                execution.current_task_index = i
                
                # Check dependencies
                if not self._check_task_dependencies(task, execution):
                    self.logger.error("Task dependencies not met", task_id=task.task_id)
                    return False
                
                # Execute task
                task_success = self._execute_task(task, execution, parameters)
                
                if task_success:
                    execution.completed_tasks.append(task.task_id)
                    self.orchestration_stats['total_tasks_executed'] += 1
                else:
                    execution.failed_tasks.append(task.task_id)
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error("Sequential execution failed", workflow_id=workflow.workflow_id, error=str(e))
            return False
    
    def _execute_parallel(self, workflow: WorkflowDefinition, execution: WorkflowExecution, 
                         parameters: Dict[str, Any]) -> bool:
        """Execute workflow in parallel"""
        try:
            # Group tasks by dependencies
            independent_tasks = [task for task in workflow.tasks if not task.dependencies and task.enabled]
            
            # Execute independent tasks in parallel
            task_threads = []
            task_results = {}
            
            for task in independent_tasks:
                task_thread = threading.Thread(
                    target=self._execute_task_thread,
                    args=(task, execution, parameters, task_results),
                    name=f"Task-{task.task_id[:8]}",
                    daemon=True
                )
                task_thread.start()
                task_threads.append(task_thread)
            
            # Wait for all tasks to complete
            for thread in task_threads:
                thread.join()
            
            # Check results
            all_success = all(task_results.values())
            
            if all_success:
                execution.completed_tasks.extend([task.task_id for task in independent_tasks])
                self.orchestration_stats['total_tasks_executed'] += len(independent_tasks)
            else:
                failed_tasks = [task_id for task_id, success in task_results.items() if not success]
                execution.failed_tasks.extend(failed_tasks)
            
            return all_success
            
        except Exception as e:
            self.logger.error("Parallel execution failed", workflow_id=workflow.workflow_id, error=str(e))
            return False
    
    def _execute_conditional(self, workflow: WorkflowDefinition, execution: WorkflowExecution, 
                            parameters: Dict[str, Any]) -> bool:
        """Execute workflow with conditions"""
        try:
            # For now, implement as sequential with condition checking
            for i, task in enumerate(workflow.tasks):
                if not task.enabled:
                    continue
                
                execution.current_task_index = i
                
                # Check conditions (simplified)
                condition_met = self._evaluate_task_condition(task, execution, parameters)
                
                if not condition_met:
                    self.logger.info("Task condition not met, skipping", task_id=task.task_id)
                    continue
                
                # Execute task
                task_success = self._execute_task(task, execution, parameters)
                
                if task_success:
                    execution.completed_tasks.append(task.task_id)
                    self.orchestration_stats['total_tasks_executed'] += 1
                else:
                    execution.failed_tasks.append(task.task_id)
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error("Conditional execution failed", workflow_id=workflow.workflow_id, error=str(e))
            return False
    
    def _execute_task_thread(self, task: OrchestrationTask, execution: WorkflowExecution, 
                            parameters: Dict[str, Any], results: Dict[str, bool]):
        """Execute task in thread"""
        try:
            success = self._execute_task(task, execution, parameters)
            results[task.task_id] = success
        except Exception as e:
            self.logger.error("Task thread execution failed", task_id=task.task_id, error=str(e))
            results[task.task_id] = False
    
    def _execute_task(self, task: OrchestrationTask, execution: WorkflowExecution, 
                     parameters: Dict[str, Any]) -> bool:
        """Execute individual task"""
        try:
            self.logger.info(
                "Task execution started",
                task_id=task.task_id,
                task_name=task.task_name,
                task_type=task.task_type.value
            )
            
            # Get task handler
            task_handler = self.task_registry.get(task.task_type.value)
            
            if not task_handler:
                self.logger.error("Task handler not found", task_type=task.task_type.value)
                return False
            
            # Execute task with retry logic
            for attempt in range(task.retry_attempts + 1):
                try:
                    result = task_handler(task, execution, parameters)
                    
                    if result:
                        execution.task_results[task.task_id] = result
                        
                        self.logger.info(
                            "Task execution completed",
                            task_id=task.task_id,
                            task_name=task.task_name,
                            attempt=attempt + 1
                        )
                        
                        return True
                    else:
                        if attempt < task.retry_attempts:
                            self.logger.warning(
                                "Task execution failed, retrying",
                                task_id=task.task_id,
                                attempt=attempt + 1,
                                max_attempts=task.retry_attempts + 1
                            )
                            time.sleep(task.retry_delay_seconds)
                        else:
                            self.logger.error("Task execution failed after all retries", task_id=task.task_id)
                            return False
                            
                except Exception as e:
                    if attempt < task.retry_attempts:
                        self.logger.warning(
                            "Task execution error, retrying",
                            task_id=task.task_id,
                            attempt=attempt + 1,
                            error=str(e)
                        )
                        time.sleep(task.retry_delay_seconds)
                    else:
                        self.logger.error("Task execution error after all retries", task_id=task.task_id, error=str(e))
                        return False
            
            return False
            
        except Exception as e:
            self.logger.error("Task execution failed", task_id=task.task_id, error=str(e))
            return False
    
    def _check_task_dependencies(self, task: OrchestrationTask, execution: WorkflowExecution) -> bool:
        """Check if task dependencies are satisfied"""
        for dependency in task.dependencies:
            if dependency not in execution.completed_tasks:
                return False
        return True
    
    def _evaluate_task_condition(self, task: OrchestrationTask, execution: WorkflowExecution, 
                                parameters: Dict[str, Any]) -> bool:
        """Evaluate task execution condition"""
        # Simplified condition evaluation
        # In a real implementation, this would parse and evaluate complex conditions
        return True
    
    # Built-in task handlers
    def _execute_deployment_task(self, task: OrchestrationTask, execution: WorkflowExecution, 
                                parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment task"""
        time.sleep(1)  # Simulate deployment
        return {'status': 'deployed', 'version': 'v1.0.0'}
    
    def _execute_integration_task(self, task: OrchestrationTask, execution: WorkflowExecution, 
                                 parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration task"""
        time.sleep(0.5)  # Simulate integration
        return {'status': 'integrated', 'endpoint': 'https://api.example.com'}
    
    def _execute_monitoring_task(self, task: OrchestrationTask, execution: WorkflowExecution, 
                                parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring task"""
        time.sleep(0.3)  # Simulate monitoring setup
        return {'status': 'monitoring_enabled', 'metrics_count': 10}
    
    def _execute_backup_task(self, task: OrchestrationTask, execution: WorkflowExecution, 
                            parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute backup task"""
        time.sleep(2)  # Simulate backup
        return {'status': 'backup_completed', 'backup_size_mb': 150}
    
    def _execute_scaling_task(self, task: OrchestrationTask, execution: WorkflowExecution, 
                             parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scaling task"""
        time.sleep(1)  # Simulate scaling
        return {'status': 'scaled', 'instances': 3}
    
    def _execute_maintenance_task(self, task: OrchestrationTask, execution: WorkflowExecution, 
                                 parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute maintenance task"""
        time.sleep(1.5)  # Simulate maintenance
        return {'status': 'maintenance_completed', 'updates_applied': 5}
    
    def _execute_testing_task(self, task: OrchestrationTask, execution: WorkflowExecution, 
                             parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute testing task"""
        time.sleep(0.8)  # Simulate testing
        return {'status': 'tests_passed', 'test_count': 25}
    
    def _execute_notification_task(self, task: OrchestrationTask, execution: WorkflowExecution, 
                                  parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification task"""
        time.sleep(0.2)  # Simulate notification
        return {'status': 'notification_sent', 'recipients': 3}
    
    def _complete_workflow_execution(self, workflow: WorkflowDefinition, execution: WorkflowExecution):
        """Complete workflow execution successfully"""
        try:
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = time.time()
            
            with self._lock:
                self.orchestration_stats['successful_executions'] += 1
                self.orchestration_stats['active_workflows'] -= 1
                
                # Update average execution time
                total_time = (
                    self.orchestration_stats['average_execution_time_minutes'] * 
                    (self.orchestration_stats['successful_executions'] - 1) +
                    (execution.get_duration() / 60)
                )
                self.orchestration_stats['average_execution_time_minutes'] = (
                    total_time / self.orchestration_stats['successful_executions']
                )
            
            # Remove from active executions
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
            
            # Collect metrics
            self.metrics_collector.collect_metric(
                name="workflow.completed",
                value=execution.get_duration(),
                metric_type=MetricType.TIMER,
                tags={
                    'workflow_id': workflow.workflow_id,
                    'mode': workflow.mode.value
                }
            )
            
            self.logger.info(
                "Workflow execution completed",
                workflow_id=workflow.workflow_id,
                execution_id=execution.execution_id,
                duration_seconds=f"{execution.get_duration():.2f}",
                completed_tasks=len(execution.completed_tasks)
            )
            
        except Exception as e:
            self.logger.error("Workflow completion failed", execution_id=execution.execution_id, error=str(e))
    
    def _fail_workflow_execution(self, workflow: WorkflowDefinition, execution: WorkflowExecution, 
                                error_message: str):
        """Fail workflow execution"""
        try:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = time.time()
            execution.error_message = error_message
            
            with self._lock:
                self.orchestration_stats['failed_executions'] += 1
                self.orchestration_stats['active_workflows'] -= 1
            
            # Remove from active executions
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
            
            self.logger.error(
                "Workflow execution failed",
                workflow_id=workflow.workflow_id,
                execution_id=execution.execution_id,
                error_message=error_message,
                duration_seconds=f"{execution.get_duration():.2f}"
            )
            
        except Exception as e:
            self.logger.error("Workflow failure handling failed", execution_id=execution.execution_id, error=str(e))
    
    def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution status"""
        if execution_id not in self.workflow_executions:
            return None
        
        execution = self.workflow_executions[execution_id]
        workflow = self.workflow_definitions.get(execution.workflow_id)
        
        status_info = {
            'execution_id': execution_id,
            'workflow_id': execution.workflow_id,
            'status': execution.status.value,
            'start_time': execution.start_time,
            'end_time': execution.end_time,
            'duration_seconds': execution.get_duration(),
            'current_task_index': execution.current_task_index,
            'completed_tasks': len(execution.completed_tasks),
            'failed_tasks': len(execution.failed_tasks),
            'error_message': execution.error_message,
            'retry_count': execution.retry_count
        }
        
        if workflow:
            status_info.update({
                'workflow_name': workflow.workflow_name,
                'total_tasks': len(workflow.tasks),
                'progress_percentage': execution.get_progress_percentage(len(workflow.tasks))
            })
        
        return status_info
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List workflow definitions"""
        workflows = []
        
        for workflow in self.workflow_definitions.values():
            workflows.append({
                'workflow_id': workflow.workflow_id,
                'workflow_name': workflow.workflow_name,
                'description': workflow.description,
                'mode': workflow.mode.value,
                'tasks_count': len(workflow.tasks),
                'enabled': workflow.enabled,
                'schedule': workflow.schedule
            })
        
        return sorted(workflows, key=lambda x: x['workflow_name'])
    
    def list_executions(self, workflow_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List workflow executions"""
        executions = []
        
        filtered_executions = self.workflow_executions.values()
        if workflow_id:
            filtered_executions = [e for e in filtered_executions if e.workflow_id == workflow_id]
        
        # Sort by start time (newest first)
        sorted_executions = sorted(filtered_executions, key=lambda x: x.start_time, reverse=True)
        
        for execution in sorted_executions[:limit]:
            execution_info = self.get_workflow_status(execution.execution_id)
            if execution_info:
                executions.append(execution_info)
        
        return executions
    
    def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel workflow execution"""
        try:
            if execution_id not in self.workflow_executions:
                self.logger.error("Workflow execution not found", execution_id=execution_id)
                return False
            
            execution = self.workflow_executions[execution_id]
            
            if execution.status not in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
                self.logger.error("Workflow cannot be cancelled", execution_id=execution_id, status=execution.status.value)
                return False
            
            # Update status
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = time.time()
            
            # Remove from active executions
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            with self._lock:
                self.orchestration_stats['active_workflows'] -= 1
            
            self.logger.info("Workflow execution cancelled", execution_id=execution_id)
            return True
            
        except Exception as e:
            self.logger.error("Workflow cancellation failed", execution_id=execution_id, error=str(e))
            return False
    
    def register_task_handler(self, task_type: str, handler: Callable) -> bool:
        """Register custom task handler"""
        try:
            self.task_registry[task_type] = handler
            self.logger.info("Task handler registered", task_type=task_type)
            return True
        except Exception as e:
            self.logger.error("Task handler registration failed", task_type=task_type, error=str(e))
            return False
    
    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration manager statistics"""
        with self._lock:
            return {
                'max_concurrent_workflows': self.max_concurrent_workflows,
                'execution_history_limit': self.execution_history_limit,
                'task_timeout_default': self.task_timeout_default,
                'scheduler_active': self.scheduler_active,
                'total_workflow_definitions': len(self.workflow_definitions),
                'total_executions': len(self.workflow_executions),
                'current_active_executions': len(self.active_executions),
                'registered_task_handlers': len(self.task_registry),
                'supported_modes': [m.value for m in OrchestrationMode],
                'supported_task_types': [t.value for t in TaskType],
                'stats': self.orchestration_stats.copy()
            }
