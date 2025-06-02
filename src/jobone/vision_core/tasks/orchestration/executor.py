"""
Task Executor for Orion Vision Core

This module provides task execution management and agent coordination.
Extracted from task_orchestration.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import asyncio
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict

from ..core.task_base import TaskDefinition, TaskStatus
from ..core.task_execution import TaskExecution
from ...agent.core.agent_logger import AgentLogger


class TaskExecutor:
    """
    Task Executor
    
    Manages task execution across multiple agents with load balancing and monitoring.
    """
    
    def __init__(self, logger: Optional[AgentLogger] = None):
        """Initialize task executor"""
        self.logger = logger or AgentLogger("task_executor")
        
        # Execution state
        self.running = False
        self.executor_task = None
        
        # Agent management
        self.available_agents: Dict[str, Dict[str, Any]] = {}  # agent_id -> agent_info
        self.agent_assignments: Dict[str, Set[str]] = defaultdict(set)  # agent_id -> task_ids
        self.task_assignments: Dict[str, str] = {}  # task_id -> agent_id
        
        # Execution tracking
        self.executing_tasks: Dict[str, TaskExecution] = {}  # task_id -> execution
        self.execution_callbacks: Dict[str, List[Callable]] = defaultdict(list)  # event -> callbacks
        
        # Performance tracking
        self.agent_performance: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'avg_execution_time': 0.0,
            'success_rate': 0.0,
            'current_load': 0.0
        })
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.executor_stats = {
            'total_tasks_executed': 0,
            'total_tasks_completed': 0,
            'total_tasks_failed': 0,
            'average_execution_time': 0.0,
            'load_balancing_efficiency': 0.0
        }
        
        self.logger.info("Task Executor initialized")
    
    async def start(self):
        """Start task executor"""
        if self.running:
            self.logger.warning("Task executor already running")
            return
        
        self.running = True
        self.executor_task = asyncio.create_task(self._execution_loop())
        
        self.logger.info("Task Executor started")
    
    async def stop(self):
        """Stop task executor"""
        if not self.running:
            self.logger.debug("Task executor not running")
            return
        
        self.running = False
        
        if self.executor_task:
            self.executor_task.cancel()
            try:
                await self.executor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Task Executor stopped")
    
    def register_agent(self, agent_id: str, capabilities: List[str], max_concurrent_tasks: int = 5):
        """Register an agent for task execution"""
        with self._lock:
            self.available_agents[agent_id] = {
                'capabilities': capabilities,
                'max_concurrent_tasks': max_concurrent_tasks,
                'registered_time': time.time(),
                'last_heartbeat': time.time(),
                'status': 'available'
            }
            
            self.logger.info(
                "Agent registered for task execution",
                agent_id=agent_id,
                capabilities=capabilities,
                max_concurrent_tasks=max_concurrent_tasks
            )
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        with self._lock:
            if agent_id in self.available_agents:
                # Cancel running tasks on this agent
                assigned_tasks = self.agent_assignments.get(agent_id, set()).copy()
                for task_id in assigned_tasks:
                    self.cancel_task_execution(task_id, "Agent unregistered")
                
                del self.available_agents[agent_id]
                if agent_id in self.agent_assignments:
                    del self.agent_assignments[agent_id]
                
                self.logger.info("Agent unregistered", agent_id=agent_id)
    
    def update_agent_heartbeat(self, agent_id: str):
        """Update agent heartbeat"""
        with self._lock:
            if agent_id in self.available_agents:
                self.available_agents[agent_id]['last_heartbeat'] = time.time()
                self.available_agents[agent_id]['status'] = 'available'
    
    def execute_task(self, task_def: TaskDefinition) -> Optional[TaskExecution]:
        """Execute task on best available agent"""
        with self._lock:
            # Find best agent for task
            best_agent = self._find_best_agent(task_def)
            if not best_agent:
                self.logger.warning(
                    "No suitable agent found for task",
                    task_id=task_def.task_id,
                    required_capabilities=task_def.required_capabilities
                )
                return None
            
            # Create execution
            execution = TaskExecution(task_id=task_def.task_id)
            execution.start_execution(best_agent, "")
            
            # Track execution
            self.executing_tasks[task_def.task_id] = execution
            self.agent_assignments[best_agent].add(task_def.task_id)
            self.task_assignments[task_def.task_id] = best_agent
            
            # Update statistics
            self.executor_stats['total_tasks_executed'] += 1
            self.agent_performance[best_agent]['total_tasks'] += 1
            self.agent_performance[best_agent]['current_load'] = len(self.agent_assignments[best_agent])
            
            self.logger.info(
                "Task execution started",
                task_id=task_def.task_id,
                task_name=task_def.task_name,
                assigned_agent=best_agent,
                agent_load=self.agent_performance[best_agent]['current_load']
            )
            
            # Trigger execution callbacks
            self._trigger_callbacks('task_started', {
                'task_id': task_def.task_id,
                'agent_id': best_agent,
                'execution': execution
            })
            
            return execution
    
    def complete_task_execution(self, task_id: str, output_data: Dict[str, Any] = None) -> bool:
        """Complete task execution"""
        with self._lock:
            if task_id not in self.executing_tasks:
                self.logger.warning("Task not found in executing tasks", task_id=task_id)
                return False
            
            execution = self.executing_tasks[task_id]
            agent_id = self.task_assignments.get(task_id)
            
            # Complete execution
            execution.complete_execution(output_data)
            
            # Update tracking
            del self.executing_tasks[task_id]
            if agent_id:
                self.agent_assignments[agent_id].discard(task_id)
                del self.task_assignments[task_id]
                
                # Update performance metrics
                self.agent_performance[agent_id]['completed_tasks'] += 1
                self.agent_performance[agent_id]['current_load'] = len(self.agent_assignments[agent_id])
                
                if execution.duration:
                    # Update average execution time
                    current_avg = self.agent_performance[agent_id]['avg_execution_time']
                    total_tasks = self.agent_performance[agent_id]['total_tasks']
                    new_avg = ((current_avg * (total_tasks - 1)) + execution.duration) / total_tasks
                    self.agent_performance[agent_id]['avg_execution_time'] = new_avg
                
                # Update success rate
                completed = self.agent_performance[agent_id]['completed_tasks']
                total = self.agent_performance[agent_id]['total_tasks']
                self.agent_performance[agent_id]['success_rate'] = completed / total if total > 0 else 0.0
            
            # Update global statistics
            self.executor_stats['total_tasks_completed'] += 1
            
            self.logger.info(
                "Task execution completed",
                task_id=task_id,
                agent_id=agent_id,
                duration=execution.duration,
                output_size=len(output_data) if output_data else 0
            )
            
            # Trigger completion callbacks
            self._trigger_callbacks('task_completed', {
                'task_id': task_id,
                'agent_id': agent_id,
                'execution': execution,
                'output_data': output_data
            })
            
            return True
    
    def fail_task_execution(self, task_id: str, error_message: str, error_details: Dict[str, Any] = None) -> bool:
        """Fail task execution"""
        with self._lock:
            if task_id not in self.executing_tasks:
                self.logger.warning("Task not found in executing tasks", task_id=task_id)
                return False
            
            execution = self.executing_tasks[task_id]
            agent_id = self.task_assignments.get(task_id)
            
            # Fail execution
            execution.fail_execution(error_message, error_details)
            
            # Update tracking
            del self.executing_tasks[task_id]
            if agent_id:
                self.agent_assignments[agent_id].discard(task_id)
                del self.task_assignments[task_id]
                
                # Update performance metrics
                self.agent_performance[agent_id]['failed_tasks'] += 1
                self.agent_performance[agent_id]['current_load'] = len(self.agent_assignments[agent_id])
                
                # Update success rate
                completed = self.agent_performance[agent_id]['completed_tasks']
                total = self.agent_performance[agent_id]['total_tasks']
                self.agent_performance[agent_id]['success_rate'] = completed / total if total > 0 else 0.0
            
            # Update global statistics
            self.executor_stats['total_tasks_failed'] += 1
            
            self.logger.error(
                "Task execution failed",
                task_id=task_id,
                agent_id=agent_id,
                error_message=error_message,
                duration=execution.duration
            )
            
            # Trigger failure callbacks
            self._trigger_callbacks('task_failed', {
                'task_id': task_id,
                'agent_id': agent_id,
                'execution': execution,
                'error_message': error_message,
                'error_details': error_details
            })
            
            return True
    
    def cancel_task_execution(self, task_id: str, reason: str = "Cancelled") -> bool:
        """Cancel task execution"""
        with self._lock:
            if task_id not in self.executing_tasks:
                self.logger.warning("Task not found in executing tasks", task_id=task_id)
                return False
            
            execution = self.executing_tasks[task_id]
            agent_id = self.task_assignments.get(task_id)
            
            # Cancel execution
            execution.cancel_execution()
            
            # Update tracking
            del self.executing_tasks[task_id]
            if agent_id:
                self.agent_assignments[agent_id].discard(task_id)
                del self.task_assignments[task_id]
                self.agent_performance[agent_id]['current_load'] = len(self.agent_assignments[agent_id])
            
            self.logger.info(
                "Task execution cancelled",
                task_id=task_id,
                agent_id=agent_id,
                reason=reason
            )
            
            # Trigger cancellation callbacks
            self._trigger_callbacks('task_cancelled', {
                'task_id': task_id,
                'agent_id': agent_id,
                'execution': execution,
                'reason': reason
            })
            
            return True
    
    def _find_best_agent(self, task_def: TaskDefinition) -> Optional[str]:
        """Find best agent for task execution"""
        best_agent = None
        best_score = -1
        
        for agent_id, agent_info in self.available_agents.items():
            # Check if agent is available
            if agent_info['status'] != 'available':
                continue
            
            # Check heartbeat (agent should be alive)
            if time.time() - agent_info['last_heartbeat'] > 30:  # 30 seconds timeout
                continue
            
            # Check capacity
            current_load = len(self.agent_assignments[agent_id])
            if current_load >= agent_info['max_concurrent_tasks']:
                continue
            
            # Check capabilities
            agent_capabilities = set(agent_info['capabilities'])
            required_capabilities = set(task_def.required_capabilities)
            if required_capabilities and not required_capabilities.issubset(agent_capabilities):
                continue
            
            # Check preferences
            if task_def.preferred_agents and agent_id not in task_def.preferred_agents:
                continue
            
            # Check exclusions
            if agent_id in task_def.excluded_agents:
                continue
            
            # Calculate score (lower load = higher score)
            load_factor = 1.0 - (current_load / agent_info['max_concurrent_tasks'])
            performance_factor = self.agent_performance[agent_id]['success_rate']
            
            score = (load_factor * 0.7) + (performance_factor * 0.3)
            
            if score > best_score:
                best_score = score
                best_agent = agent_id
        
        return best_agent
    
    def add_execution_callback(self, event: str, callback: Callable):
        """Add execution event callback"""
        self.execution_callbacks[event].append(callback)
        self.logger.debug("Execution callback added", event=event, callback_name=callback.__name__)
    
    def _trigger_callbacks(self, event: str, data: Dict[str, Any]):
        """Trigger execution callbacks"""
        for callback in self.execution_callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(
                    "Execution callback failed",
                    event=event,
                    callback_name=callback.__name__,
                    error=str(e)
                )
    
    async def _execution_loop(self):
        """Main execution monitoring loop"""
        while self.running:
            try:
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
                if not self.running:
                    break
                
                # Check agent health
                await self._check_agent_health()
                
                # Update load balancing efficiency
                self._update_load_balancing_efficiency()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Execution loop error", error=str(e))
    
    async def _check_agent_health(self):
        """Check agent health and mark unhealthy agents"""
        with self._lock:
            current_time = time.time()
            unhealthy_agents = []
            
            for agent_id, agent_info in self.available_agents.items():
                if current_time - agent_info['last_heartbeat'] > 60:  # 1 minute timeout
                    unhealthy_agents.append(agent_id)
            
            # Mark unhealthy agents and reassign their tasks
            for agent_id in unhealthy_agents:
                self.available_agents[agent_id]['status'] = 'unhealthy'
                
                # Cancel tasks on unhealthy agent
                assigned_tasks = self.agent_assignments.get(agent_id, set()).copy()
                for task_id in assigned_tasks:
                    self.cancel_task_execution(task_id, "Agent unhealthy")
                
                self.logger.warning("Agent marked as unhealthy", agent_id=agent_id)
    
    def _update_load_balancing_efficiency(self):
        """Update load balancing efficiency metric"""
        with self._lock:
            if not self.available_agents:
                return
            
            loads = [len(self.agent_assignments[agent_id]) for agent_id in self.available_agents]
            if not loads:
                return
            
            avg_load = sum(loads) / len(loads)
            max_load = max(loads)
            min_load = min(loads)
            
            # Efficiency = 1 - (variance / max_possible_variance)
            if max_load > 0:
                variance = sum((load - avg_load) ** 2 for load in loads) / len(loads)
                max_variance = ((max_load - 0) ** 2) / 2  # Theoretical max variance
                efficiency = 1.0 - (variance / max_variance) if max_variance > 0 else 1.0
                self.executor_stats['load_balancing_efficiency'] = max(0.0, min(1.0, efficiency))
    
    def get_executor_stats(self) -> Dict[str, Any]:
        """Get executor statistics"""
        with self._lock:
            return {
                'running': self.running,
                'available_agents': len(self.available_agents),
                'executing_tasks': len(self.executing_tasks),
                'stats': self.executor_stats.copy(),
                'agent_performance': {
                    agent_id: perf.copy() for agent_id, perf in self.agent_performance.items()
                }
            }
