"""
Workflow Engine for Orion Vision Core

This module provides workflow execution and management capabilities.
Extracted from task_orchestration.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..core.task_base import TaskDefinition, TaskStatus, WorkflowStatus
from ..core.task_execution import TaskExecution
from ...agent.core.agent_logger import AgentLogger


@dataclass
class WorkflowStep:
    """Individual workflow step definition"""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_name: str = ""
    step_type: str = "task"
    task_definition: Optional[TaskDefinition] = None
    
    # Step dependencies
    depends_on: List[str] = field(default_factory=list)  # step_ids
    
    # Conditional execution
    condition: Optional[str] = None  # Python expression
    condition_data: Dict[str, Any] = field(default_factory=dict)
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Step metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate step after initialization"""
        if not self.step_name:
            raise ValueError("step_name cannot be empty")
        if self.step_type == "task" and not self.task_definition:
            raise ValueError("task_definition required for task steps")


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_name: str = ""
    description: str = ""
    version: str = "1.0.0"
    
    # Workflow steps
    steps: List[WorkflowStep] = field(default_factory=list)
    
    # Workflow configuration
    timeout: float = 3600.0  # 1 hour default
    max_parallel_steps: int = 5
    failure_strategy: str = "stop"  # stop, continue, retry
    
    # Workflow metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_time: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validate workflow after initialization"""
        if not self.workflow_name:
            raise ValueError("workflow_name cannot be empty")
        # Note: steps validation moved to validate() method for builder compatibility
    
    def add_step(self, step: WorkflowStep):
        """Add step to workflow"""
        self.steps.append(step)
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def validate(self) -> bool:
        """Validate complete workflow"""
        if not self.workflow_name:
            return False
        if not self.steps:
            return False
        return self.validate_dependencies()

    def validate_dependencies(self) -> bool:
        """Validate step dependencies"""
        step_ids = {step.step_id for step in self.steps}

        for step in self.steps:
            for dep_id in step.depends_on:
                if dep_id not in step_ids:
                    return False
        return True


@dataclass
class WorkflowExecution:
    """Workflow execution state tracking"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    workflow_name: str = ""
    
    # Execution state
    status: WorkflowStatus = WorkflowStatus.CREATED
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    
    # Step execution tracking
    step_executions: Dict[str, TaskExecution] = field(default_factory=dict)  # step_id -> execution
    step_status: Dict[str, str] = field(default_factory=dict)  # step_id -> status
    step_results: Dict[str, Any] = field(default_factory=dict)  # step_id -> result
    
    # Progress tracking
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    progress_percentage: float = 0.0
    
    # Error tracking
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    def start_execution(self):
        """Start workflow execution"""
        self.status = WorkflowStatus.RUNNING
        self.start_time = time.time()
        self.progress_percentage = 0.0
    
    def complete_execution(self):
        """Complete workflow execution"""
        self.status = WorkflowStatus.COMPLETED
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.progress_percentage = 100.0
    
    def fail_execution(self, error_message: str):
        """Fail workflow execution"""
        self.status = WorkflowStatus.FAILED
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        
        self.errors.append({
            'timestamp': time.time(),
            'message': error_message,
            'type': 'workflow_failure'
        })
    
    def update_progress(self):
        """Update workflow progress"""
        if self.total_steps > 0:
            self.progress_percentage = (self.completed_steps / self.total_steps) * 100.0


class WorkflowEngine:
    """
    Workflow Engine
    
    Executes workflows with step dependencies, parallel execution, and error handling.
    """
    
    def __init__(self, logger: Optional[AgentLogger] = None):
        """Initialize workflow engine"""
        self.logger = logger or AgentLogger("workflow_engine")
        
        # Engine state
        self.running = False
        self.engine_task = None
        
        # Workflow storage
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.completed_executions: Dict[str, WorkflowExecution] = {}
        
        # Execution callbacks
        self.execution_callbacks: Dict[str, List[Callable]] = {
            'workflow_started': [],
            'workflow_completed': [],
            'workflow_failed': [],
            'step_started': [],
            'step_completed': [],
            'step_failed': []
        }
        
        # Statistics
        self.engine_stats = {
            'total_workflows_executed': 0,
            'total_workflows_completed': 0,
            'total_workflows_failed': 0,
            'total_steps_executed': 0,
            'average_workflow_duration': 0.0,
            'success_rate': 0.0
        }
        
        self.logger.info("Workflow Engine initialized")
    
    async def start(self):
        """Start workflow engine"""
        if self.running:
            self.logger.warning("Workflow engine already running")
            return
        
        self.running = True
        self.engine_task = asyncio.create_task(self._engine_loop())
        
        self.logger.info("Workflow Engine started")
    
    async def stop(self):
        """Stop workflow engine"""
        if not self.running:
            self.logger.debug("Workflow engine not running")
            return
        
        self.running = False
        
        if self.engine_task:
            self.engine_task.cancel()
            try:
                await self.engine_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Workflow Engine stopped")
    
    def register_workflow(self, workflow_def: WorkflowDefinition) -> bool:
        """Register workflow definition"""
        try:
            # Validate workflow
            if not workflow_def.validate_dependencies():
                self.logger.error(
                    "Invalid workflow dependencies",
                    workflow_id=workflow_def.workflow_id,
                    workflow_name=workflow_def.workflow_name
                )
                return False
            
            self.workflow_definitions[workflow_def.workflow_id] = workflow_def
            
            self.logger.info(
                "Workflow registered",
                workflow_id=workflow_def.workflow_id,
                workflow_name=workflow_def.workflow_name,
                steps_count=len(workflow_def.steps)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Workflow registration failed",
                workflow_id=workflow_def.workflow_id,
                error=str(e)
            )
            return False
    
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None) -> Optional[str]:
        """Execute workflow"""
        if workflow_id not in self.workflow_definitions:
            self.logger.error("Workflow not found", workflow_id=workflow_id)
            return None
        
        workflow_def = self.workflow_definitions[workflow_id]
        
        # Create execution
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            workflow_name=workflow_def.workflow_name,
            total_steps=len(workflow_def.steps)
        )
        
        execution.start_execution()
        self.active_executions[execution.execution_id] = execution
        
        self.logger.info(
            "Workflow execution started",
            execution_id=execution.execution_id,
            workflow_id=workflow_id,
            workflow_name=workflow_def.workflow_name
        )
        
        # Trigger callbacks
        self._trigger_callbacks('workflow_started', {
            'execution_id': execution.execution_id,
            'workflow_id': workflow_id,
            'input_data': input_data
        })
        
        # Start execution task
        asyncio.create_task(self._execute_workflow_steps(execution, workflow_def, input_data or {}))
        
        return execution.execution_id
    
    async def _execute_workflow_steps(self, execution: WorkflowExecution, 
                                    workflow_def: WorkflowDefinition, 
                                    input_data: Dict[str, Any]):
        """Execute workflow steps"""
        try:
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(workflow_def)
            
            # Execute steps in dependency order
            executed_steps = set()
            
            while len(executed_steps) < len(workflow_def.steps):
                # Find ready steps
                ready_steps = []
                for step in workflow_def.steps:
                    if step.step_id not in executed_steps:
                        if all(dep_id in executed_steps for dep_id in step.depends_on):
                            ready_steps.append(step)
                
                if not ready_steps:
                    # Circular dependency or other issue
                    execution.fail_execution("No ready steps found - possible circular dependency")
                    break
                
                # Execute ready steps (up to max_parallel_steps)
                parallel_limit = min(len(ready_steps), workflow_def.max_parallel_steps)
                step_tasks = []
                
                for i in range(parallel_limit):
                    step = ready_steps[i]
                    task = asyncio.create_task(self._execute_step(execution, step, input_data))
                    step_tasks.append((step.step_id, task))
                
                # Wait for step completion
                for step_id, task in step_tasks:
                    try:
                        await task
                        executed_steps.add(step_id)
                        execution.completed_steps += 1
                    except Exception as e:
                        execution.failed_steps += 1
                        execution.errors.append({
                            'timestamp': time.time(),
                            'step_id': step_id,
                            'message': str(e),
                            'type': 'step_failure'
                        })
                        
                        if workflow_def.failure_strategy == "stop":
                            execution.fail_execution(f"Step {step_id} failed: {e}")
                            return
                
                execution.update_progress()
            
            # Complete workflow
            if execution.failed_steps == 0:
                execution.complete_execution()
                self.engine_stats['total_workflows_completed'] += 1
                
                self.logger.info(
                    "Workflow execution completed",
                    execution_id=execution.execution_id,
                    duration=execution.duration,
                    completed_steps=execution.completed_steps
                )
                
                self._trigger_callbacks('workflow_completed', {
                    'execution_id': execution.execution_id,
                    'execution': execution
                })
            else:
                execution.fail_execution(f"Workflow completed with {execution.failed_steps} failed steps")
                self.engine_stats['total_workflows_failed'] += 1
                
                self._trigger_callbacks('workflow_failed', {
                    'execution_id': execution.execution_id,
                    'execution': execution
                })
            
        except Exception as e:
            execution.fail_execution(f"Workflow execution error: {e}")
            self.engine_stats['total_workflows_failed'] += 1
            
            self.logger.error(
                "Workflow execution failed",
                execution_id=execution.execution_id,
                error=str(e)
            )
            
            self._trigger_callbacks('workflow_failed', {
                'execution_id': execution.execution_id,
                'execution': execution,
                'error': str(e)
            })
        
        finally:
            # Move to completed
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
            self.completed_executions[execution.execution_id] = execution
            
            self.engine_stats['total_workflows_executed'] += 1
    
    async def _execute_step(self, execution: WorkflowExecution, step: WorkflowStep, context_data: Dict[str, Any]):
        """Execute individual workflow step"""
        self.logger.info(
            "Step execution started",
            execution_id=execution.execution_id,
            step_id=step.step_id,
            step_name=step.step_name
        )
        
        # Trigger step started callback
        self._trigger_callbacks('step_started', {
            'execution_id': execution.execution_id,
            'step_id': step.step_id,
            'step': step
        })
        
        try:
            # Check condition if present
            if step.condition:
                if not self._evaluate_condition(step.condition, context_data):
                    execution.step_status[step.step_id] = "skipped"
                    self.logger.info("Step skipped due to condition", step_id=step.step_id)
                    return
            
            # Execute step based on type
            if step.step_type == "task" and step.task_definition:
                # Create task execution
                task_execution = TaskExecution(task_id=step.task_definition.task_id)
                task_execution.start_execution("workflow_engine", execution.execution_id)
                
                execution.step_executions[step.step_id] = task_execution
                
                # Simulate task execution (in real implementation, this would delegate to TaskExecutor)
                await asyncio.sleep(0.1)  # Simulate work
                
                # Complete task
                result = {"step_result": f"Step {step.step_name} completed"}
                task_execution.complete_execution(result)
                execution.step_results[step.step_id] = result
                execution.step_status[step.step_id] = "completed"
                
                self.engine_stats['total_steps_executed'] += 1
                
                self.logger.info(
                    "Step execution completed",
                    execution_id=execution.execution_id,
                    step_id=step.step_id,
                    duration=task_execution.duration
                )
                
                self._trigger_callbacks('step_completed', {
                    'execution_id': execution.execution_id,
                    'step_id': step.step_id,
                    'result': result
                })
            
        except Exception as e:
            execution.step_status[step.step_id] = "failed"
            
            self.logger.error(
                "Step execution failed",
                execution_id=execution.execution_id,
                step_id=step.step_id,
                error=str(e)
            )
            
            self._trigger_callbacks('step_failed', {
                'execution_id': execution.execution_id,
                'step_id': step.step_id,
                'error': str(e)
            })
            
            raise
    
    def _build_dependency_graph(self, workflow_def: WorkflowDefinition) -> Dict[str, List[str]]:
        """Build step dependency graph"""
        graph = {}
        for step in workflow_def.steps:
            graph[step.step_id] = step.depends_on.copy()
        return graph
    
    def _evaluate_condition(self, condition: str, context_data: Dict[str, Any]) -> bool:
        """Evaluate step condition"""
        try:
            # Simple condition evaluation (in production, use safer evaluation)
            return eval(condition, {"__builtins__": {}}, context_data)
        except Exception:
            return False
    
    def add_callback(self, event: str, callback: Callable):
        """Add execution callback"""
        if event in self.execution_callbacks:
            self.execution_callbacks[event].append(callback)
            self.logger.debug("Callback added", event=event, callback_name=callback.__name__)
    
    def _trigger_callbacks(self, event: str, data: Dict[str, Any]):
        """Trigger execution callbacks"""
        for callback in self.execution_callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(
                    "Callback execution failed",
                    event=event,
                    callback_name=callback.__name__,
                    error=str(e)
                )
    
    async def _engine_loop(self):
        """Main engine monitoring loop"""
        while self.running:
            try:
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
                if not self.running:
                    break
                
                # Update statistics
                self._update_statistics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Engine loop error", error=str(e))
    
    def _update_statistics(self):
        """Update engine statistics"""
        total_executed = self.engine_stats['total_workflows_executed']
        if total_executed > 0:
            completed = self.engine_stats['total_workflows_completed']
            self.engine_stats['success_rate'] = (completed / total_executed) * 100.0
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            'running': self.running,
            'active_executions': len(self.active_executions),
            'completed_executions': len(self.completed_executions),
            'registered_workflows': len(self.workflow_definitions),
            'stats': self.engine_stats.copy()
        }
