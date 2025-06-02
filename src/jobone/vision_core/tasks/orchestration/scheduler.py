"""
Task Scheduler for Orion Vision Core

This module provides intelligent task scheduling with priority and dependency management.
Extracted from task_orchestration.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import asyncio
import time
import threading
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict, deque

from ..core.task_base import TaskDefinition, TaskPriority, TaskStatus
from ..core.task_execution import TaskExecution
from ...agent.core.agent_logger import AgentLogger


class TaskScheduler:
    """
    Intelligent Task Scheduler
    
    Schedules tasks based on priority, dependencies, and agent availability.
    """
    
    def __init__(self, logger: Optional[AgentLogger] = None):
        """Initialize task scheduler"""
        self.logger = logger or AgentLogger("task_scheduler")
        
        # Task queues by priority
        self.task_queues: Dict[TaskPriority, deque] = {
            priority: deque() for priority in TaskPriority
        }
        
        # Task storage
        self.pending_tasks: Dict[str, TaskDefinition] = {}
        self.running_tasks: Dict[str, TaskExecution] = {}
        self.completed_tasks: Dict[str, TaskExecution] = {}
        
        # Dependency tracking
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.dependent_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # Scheduling state
        self.running = False
        self.scheduler_task = None
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.scheduler_stats = {
            'total_tasks_scheduled': 0,
            'total_tasks_completed': 0,
            'total_tasks_failed': 0,
            'average_scheduling_time': 0.0,
            'average_execution_time': 0.0
        }
        
        self.logger.info("Task Scheduler initialized")
    
    async def start(self):
        """Start task scheduler"""
        if self.running:
            self.logger.warning("Task scheduler already running")
            return
        
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduling_loop())
        
        self.logger.info("Task Scheduler started")
    
    async def stop(self):
        """Stop task scheduler"""
        if not self.running:
            self.logger.debug("Task scheduler not running")
            return
        
        self.running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Task Scheduler stopped")
    
    def submit_task(self, task_definition: TaskDefinition) -> bool:
        """Submit task to scheduler"""
        with self._lock:
            try:
                # Validate task definition
                if not task_definition.validate():
                    self.logger.error(
                        "Invalid task definition",
                        task_id=task_definition.task_id,
                        task_name=task_definition.task_name
                    )
                    return False
                
                # Add to pending tasks
                self.pending_tasks[task_definition.task_id] = task_definition
                
                # Add to priority queue
                self.task_queues[task_definition.priority].append(task_definition.task_id)
                
                # Update dependency graph
                for dep_task_id in task_definition.dependencies:
                    self.dependency_graph[task_definition.task_id].add(dep_task_id)
                    self.dependent_graph[dep_task_id].add(task_definition.task_id)
                
                self.scheduler_stats['total_tasks_scheduled'] += 1
                
                self.logger.info(
                    "Task submitted to scheduler",
                    task_id=task_definition.task_id,
                    task_name=task_definition.task_name,
                    priority=task_definition.priority.name,
                    dependencies_count=len(task_definition.dependencies)
                )
                
                return True
                
            except Exception as e:
                self.logger.error(
                    "Task submission failed",
                    task_id=task_definition.task_id,
                    error=str(e)
                )
                return False
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel task"""
        with self._lock:
            try:
                # Cancel pending task
                if task_id in self.pending_tasks:
                    task_def = self.pending_tasks[task_id]
                    
                    # Remove from queue
                    try:
                        self.task_queues[task_def.priority].remove(task_id)
                    except ValueError:
                        pass
                    
                    # Remove from pending
                    del self.pending_tasks[task_id]
                    
                    self.logger.info("Pending task cancelled", task_id=task_id)
                    return True
                
                # Cancel running task
                if task_id in self.running_tasks:
                    execution = self.running_tasks[task_id]
                    execution.cancel_execution()
                    
                    # Move to completed
                    self.completed_tasks[task_id] = execution
                    del self.running_tasks[task_id]
                    
                    self.logger.info("Running task cancelled", task_id=task_id)
                    return True
                
                self.logger.warning("Task not found for cancellation", task_id=task_id)
                return False
                
            except Exception as e:
                self.logger.error("Task cancellation failed", task_id=task_id, error=str(e))
                return False
    
    def get_next_task(self) -> Optional[TaskDefinition]:
        """Get next task to execute"""
        with self._lock:
            # Check priorities (highest first)
            for priority in sorted(TaskPriority, key=lambda p: p.value, reverse=True):
                queue = self.task_queues[priority]
                
                while queue:
                    task_id = queue.popleft()
                    
                    # Check if task still pending
                    if task_id not in self.pending_tasks:
                        continue
                    
                    task_def = self.pending_tasks[task_id]
                    
                    # Check dependencies
                    if self._are_dependencies_satisfied(task_id):
                        # Check scheduled time
                        if task_def.scheduled_time and time.time() < task_def.scheduled_time:
                            queue.append(task_id)  # Put back
                            continue
                        
                        # Check deadline
                        if task_def.is_expired():
                            self.logger.warning(
                                "Task expired, removing from queue",
                                task_id=task_id,
                                deadline=task_def.deadline
                            )
                            del self.pending_tasks[task_id]
                            continue
                        
                        # Task is ready
                        del self.pending_tasks[task_id]
                        
                        self.logger.info(
                            "Next task selected for execution",
                            task_id=task_id,
                            task_name=task_def.task_name,
                            priority=priority.name
                        )
                        
                        return task_def
                    else:
                        # Dependencies not satisfied, put back
                        queue.append(task_id)
            
            return None
    
    def _are_dependencies_satisfied(self, task_id: str) -> bool:
        """Check if task dependencies are satisfied"""
        dependencies = self.dependency_graph.get(task_id, set())
        
        for dep_task_id in dependencies:
            if dep_task_id in self.completed_tasks:
                execution = self.completed_tasks[dep_task_id]
                if execution.status != TaskStatus.COMPLETED:
                    return False  # Dependency failed
            else:
                return False  # Dependency not completed
        
        return True
    
    def start_task_execution(self, task_def: TaskDefinition, agent_id: str, service_id: str = "") -> TaskExecution:
        """Start task execution"""
        with self._lock:
            execution = TaskExecution(task_id=task_def.task_id)
            execution.start_execution(agent_id, service_id)
            
            self.running_tasks[task_def.task_id] = execution
            
            self.logger.info(
                "Task execution started",
                task_id=task_def.task_id,
                task_name=task_def.task_name,
                agent_id=agent_id,
                service_id=service_id
            )
            
            return execution
    
    def complete_task_execution(self, task_id: str, output_data: Dict[str, Any] = None) -> bool:
        """Complete task execution"""
        with self._lock:
            if task_id not in self.running_tasks:
                self.logger.warning("Task not found in running tasks", task_id=task_id)
                return False
            
            execution = self.running_tasks[task_id]
            execution.complete_execution(output_data)
            
            # Move to completed
            self.completed_tasks[task_id] = execution
            del self.running_tasks[task_id]
            
            self.scheduler_stats['total_tasks_completed'] += 1
            
            # Check dependent tasks
            self._check_dependent_tasks(task_id)
            
            self.logger.info(
                "Task execution completed",
                task_id=task_id,
                duration=execution.duration,
                output_size=len(output_data) if output_data else 0
            )
            
            return True
    
    def fail_task_execution(self, task_id: str, error_message: str, error_details: Dict[str, Any] = None) -> bool:
        """Fail task execution"""
        with self._lock:
            if task_id not in self.running_tasks:
                self.logger.warning("Task not found in running tasks", task_id=task_id)
                return False
            
            execution = self.running_tasks[task_id]
            execution.fail_execution(error_message, error_details)
            
            # Move to completed
            self.completed_tasks[task_id] = execution
            del self.running_tasks[task_id]
            
            self.scheduler_stats['total_tasks_failed'] += 1
            
            self.logger.error(
                "Task execution failed",
                task_id=task_id,
                error_message=error_message,
                duration=execution.duration
            )
            
            return True
    
    def _check_dependent_tasks(self, completed_task_id: str):
        """Check dependent tasks after completion"""
        dependents = self.dependent_graph.get(completed_task_id, set())
        
        for dependent_task_id in dependents:
            if dependent_task_id in self.pending_tasks:
                if self._are_dependencies_satisfied(dependent_task_id):
                    task_def = self.pending_tasks[dependent_task_id]
                    if dependent_task_id not in self.task_queues[task_def.priority]:
                        self.task_queues[task_def.priority].append(dependent_task_id)
    
    async def _scheduling_loop(self):
        """Main scheduling loop"""
        while self.running:
            try:
                await asyncio.sleep(1.0)
                
                if not self.running:
                    break
                
                # Check timeouts and deadlines
                await self._check_task_timeouts()
                await self._check_task_deadlines()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Scheduling loop error", error=str(e))
    
    async def _check_task_timeouts(self):
        """Check for timed out tasks"""
        with self._lock:
            current_time = time.time()
            timeout_tasks = []
            
            for task_id, execution in self.running_tasks.items():
                if execution.start_time:
                    # Find task definition to get timeout
                    runtime = current_time - execution.start_time
                    # Default timeout if not found
                    timeout = 300.0  # 5 minutes
                    
                    if runtime > timeout:
                        timeout_tasks.append(task_id)
            
            # Handle timeouts
            for task_id in timeout_tasks:
                execution = self.running_tasks[task_id]
                execution.timeout_execution()
                self.completed_tasks[task_id] = execution
                del self.running_tasks[task_id]
                
                self.logger.warning("Task timed out", task_id=task_id)
    
    async def _check_task_deadlines(self):
        """Check for tasks past deadline"""
        with self._lock:
            current_time = time.time()
            deadline_tasks = []
            
            for task_id, task_def in self.pending_tasks.items():
                if task_def.deadline and current_time > task_def.deadline:
                    deadline_tasks.append(task_id)
            
            # Cancel expired tasks
            for task_id in deadline_tasks:
                self.cancel_task(task_id)
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        with self._lock:
            return {
                'running': self.running,
                'pending_tasks': len(self.pending_tasks),
                'running_tasks': len(self.running_tasks),
                'completed_tasks': len(self.completed_tasks),
                'stats': self.scheduler_stats.copy(),
                'queue_sizes': {
                    priority.name: len(queue) for priority, queue in self.task_queues.items()
                }
            }
