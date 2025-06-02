#!/usr/bin/env python3
"""
Automation Controller - Advanced Automation Orchestration
Sprint 8.4 - Advanced Task Automation and AI-Driven Workflows
Orion Vision Core - Autonomous AI Operating System

This module provides advanced automation orchestration capabilities including
intelligent scheduling, resource management, and adaptive automation for the
Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.4.0
Date: 30 Mayıs 2025
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from ..workflows.workflow_engine import get_workflow_engine
from ..tasks.task_framework import get_task_manager
from .ai_optimizer import get_ai_optimizer
from ..brain.brain_ai_manager import get_brain_ai_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutomationController")

class AutomationMode(Enum):
    """Automation mode enumeration"""
    MANUAL = "manual"
    SEMI_AUTOMATIC = "semi_automatic"
    FULLY_AUTOMATIC = "fully_automatic"
    ADAPTIVE = "adaptive"

class ScheduleType(Enum):
    """Schedule type enumeration"""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    RECURRING = "recurring"
    CONDITIONAL = "conditional"
    EVENT_DRIVEN = "event_driven"

class ResourceType(Enum):
    """Resource type enumeration"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    CUSTOM = "custom"

@dataclass
class AutomationRule:
    """Automation rule definition"""
    rule_id: str
    name: str
    description: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    schedule: Dict[str, Any]
    priority: int
    enabled: bool
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    failure_handling: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AutomationExecution:
    """Automation execution record"""
    execution_id: str
    rule: AutomationRule
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    triggered_by: str
    execution_context: Dict[str, Any]
    results: List[Any]
    errors: List[str]
    resource_usage: Dict[str, float]
    performance_metrics: Dict[str, float]

class AutomationController(QObject):
    """
    Advanced automation orchestration controller.
    
    Features:
    - Intelligent automation scheduling
    - Resource-aware execution
    - Adaptive automation strategies
    - Event-driven automation
    - Performance optimization
    - Comprehensive monitoring
    """
    
    # Signals
    automation_triggered = pyqtSignal(str, str)  # rule_id, trigger_reason
    automation_completed = pyqtSignal(str, dict)  # execution_id, results
    automation_failed = pyqtSignal(str, str)  # execution_id, error
    resource_allocated = pyqtSignal(str, dict)  # execution_id, resources
    optimization_applied = pyqtSignal(str, dict)  # rule_id, optimization
    
    def __init__(self):
        """Initialize Automation Controller"""
        super().__init__()
        
        # Component references
        self.workflow_engine = get_workflow_engine()
        self.task_manager = get_task_manager()
        self.ai_optimizer = get_ai_optimizer()
        self.brain_manager = get_brain_ai_manager()
        
        # Automation configuration
        self.automation_mode = AutomationMode.ADAPTIVE
        self.max_concurrent_automations = 5
        self.resource_allocation_enabled = True
        self.optimization_enabled = True
        
        # Automation management
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.active_executions: Dict[str, AutomationExecution] = {}
        self.execution_history: List[AutomationExecution] = []
        self.rule_counter = 0
        self.execution_counter = 0
        
        # Resource management
        self.available_resources = {
            ResourceType.CPU: 100.0,
            ResourceType.MEMORY: 100.0,
            ResourceType.STORAGE: 100.0,
            ResourceType.NETWORK: 100.0,
            ResourceType.GPU: 100.0
        }
        self.allocated_resources: Dict[str, Dict[ResourceType, float]] = {}
        
        # Scheduling and monitoring
        self.scheduler_timer = QTimer()
        self.scheduler_timer.timeout.connect(self._process_scheduled_automations)
        self.scheduler_timer.start(5000)  # Check every 5 seconds
        
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_automations)
        self.monitor_timer.start(10000)  # Monitor every 10 seconds
        
        # Statistics
        self.automation_stats = {
            'total_rules': 0,
            'active_rules': 0,
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'resource_efficiency': 0.0,
            'automation_success_rate': 0.0
        }
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        logger.info("🤖 Automation Controller initialized")
    
    def create_automation_rule(self, name: str, description: str,
                              trigger_conditions: Dict[str, Any],
                              actions: List[Dict[str, Any]],
                              schedule: Dict[str, Any] = None,
                              priority: int = 5) -> str:
        """
        Create a new automation rule.
        
        Args:
            name: Rule name
            description: Rule description
            trigger_conditions: Conditions that trigger the automation
            actions: Actions to execute when triggered
            schedule: Schedule configuration
            priority: Rule priority (1-10, higher is more important)
            
        Returns:
            Rule ID
        """
        try:
            rule_id = self._generate_rule_id()
            
            # Default schedule if not provided
            if schedule is None:
                schedule = {'type': 'immediate'}
            
            # Create automation rule
            rule = AutomationRule(
                rule_id=rule_id,
                name=name,
                description=description,
                trigger_conditions=trigger_conditions,
                actions=actions,
                schedule=schedule,
                priority=priority,
                enabled=True,
                metadata={'created_at': datetime.now().isoformat()}
            )
            
            # Validate rule
            if not self._validate_automation_rule(rule):
                logger.error(f"❌ Automation rule validation failed: {rule_id}")
                return None
            
            # Store rule
            self.automation_rules[rule_id] = rule
            
            # Update statistics
            self.automation_stats['total_rules'] += 1
            self.automation_stats['active_rules'] += 1
            
            logger.info(f"🤖 Created automation rule: {name} (ID: {rule_id})")
            return rule_id
            
        except Exception as e:
            logger.error(f"❌ Error creating automation rule: {e}")
            return None
    
    async def trigger_automation(self, rule_id: str, trigger_context: Dict[str, Any] = None) -> str:
        """
        Trigger an automation rule.
        
        Args:
            rule_id: Rule ID to trigger
            trigger_context: Context information for the trigger
            
        Returns:
            Execution ID if successful, None otherwise
        """
        try:
            if rule_id not in self.automation_rules:
                logger.error(f"❌ Automation rule not found: {rule_id}")
                return None
            
            rule = self.automation_rules[rule_id]
            
            if not rule.enabled:
                logger.warning(f"⚠️ Automation rule is disabled: {rule_id}")
                return None
            
            # Check resource availability
            if not self._check_resource_availability(rule):
                logger.warning(f"⚠️ Insufficient resources for automation: {rule_id}")
                return None
            
            # Check concurrent execution limit
            if len(self.active_executions) >= self.max_concurrent_automations:
                logger.warning(f"⚠️ Maximum concurrent automations reached: {self.max_concurrent_automations}")
                return None
            
            # Create execution record
            execution_id = self._generate_execution_id()
            execution = AutomationExecution(
                execution_id=execution_id,
                rule=rule,
                status="running",
                start_time=datetime.now(),
                end_time=None,
                triggered_by=trigger_context.get('triggered_by', 'manual') if trigger_context else 'manual',
                execution_context=trigger_context or {},
                results=[],
                errors=[],
                resource_usage={},
                performance_metrics={}
            )
            
            # Allocate resources
            if self.resource_allocation_enabled:
                allocated = self._allocate_resources(execution_id, rule)
                if allocated:
                    self.resource_allocated.emit(execution_id, allocated)
            
            # Add to active executions
            self.active_executions[execution_id] = execution
            
            # Emit trigger signal
            trigger_reason = trigger_context.get('reason', 'manual trigger') if trigger_context else 'manual trigger'
            self.automation_triggered.emit(rule_id, trigger_reason)
            
            # Execute automation
            success = await self._execute_automation(execution)
            
            # Complete execution
            self._complete_automation_execution(execution, success)
            
            return execution_id
            
        except Exception as e:
            logger.error(f"❌ Error triggering automation: {e}")
            return None
    
    async def _execute_automation(self, execution: AutomationExecution) -> bool:
        """Execute automation actions"""
        try:
            rule = execution.rule
            success_count = 0
            total_actions = len(rule.actions)
            
            for i, action in enumerate(rule.actions):
                try:
                    action_type = action.get('type')
                    action_params = action.get('parameters', {})
                    
                    # Execute action based on type
                    if action_type == 'workflow':
                        result = await self._execute_workflow_action(action_params, execution)
                    elif action_type == 'task':
                        result = await self._execute_task_action(action_params, execution)
                    elif action_type == 'system_command':
                        result = await self._execute_command_action(action_params, execution)
                    elif action_type == 'notification':
                        result = await self._execute_notification_action(action_params, execution)
                    elif action_type == 'custom':
                        result = await self._execute_custom_action(action_params, execution)
                    else:
                        logger.warning(f"⚠️ Unknown action type: {action_type}")
                        result = {'success': False, 'error': f'Unknown action type: {action_type}'}
                    
                    # Store result
                    execution.results.append(result)
                    
                    if result.get('success', False):
                        success_count += 1
                    else:
                        execution.errors.append(result.get('error', 'Action failed'))
                        
                        # Check failure handling
                        failure_strategy = rule.failure_handling.get('strategy', 'continue')
                        if failure_strategy == 'stop_on_failure':
                            break
                    
                except Exception as e:
                    error_msg = f"Action {i+1} failed: {e}"
                    execution.errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            # Calculate success rate
            success_rate = success_count / total_actions if total_actions > 0 else 0.0
            execution.performance_metrics['success_rate'] = success_rate
            
            # Check success criteria
            success_threshold = rule.success_criteria.get('min_success_rate', 0.8)
            return success_rate >= success_threshold
            
        except Exception as e:
            logger.error(f"❌ Error executing automation: {e}")
            execution.errors.append(f"Execution error: {e}")
            return False
    
    async def _execute_workflow_action(self, params: Dict[str, Any], 
                                     execution: AutomationExecution) -> Dict[str, Any]:
        """Execute workflow action"""
        try:
            workflow_definition = params.get('workflow_definition')
            optimization_strategy = params.get('optimization_strategy', 'balanced')
            
            if not workflow_definition:
                return {'success': False, 'error': 'No workflow definition provided'}
            
            # Create workflow
            workflow_id = self.workflow_engine.create_workflow(
                name=f"Automation_{execution.execution_id}_Workflow",
                description=f"Workflow for automation rule {execution.rule.rule_id}",
                workflow_definition=workflow_definition,
                optimization_strategy=optimization_strategy
            )
            
            if not workflow_id:
                return {'success': False, 'error': 'Failed to create workflow'}
            
            # Execute workflow (simplified - in real implementation would wait for completion)
            workflow_success = await self.workflow_engine.execute_workflow(workflow_id)
            
            return {
                'success': workflow_success,
                'workflow_id': workflow_id,
                'type': 'workflow'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'type': 'workflow'}
    
    async def _execute_task_action(self, params: Dict[str, Any], 
                                 execution: AutomationExecution) -> Dict[str, Any]:
        """Execute task action"""
        try:
            task_definition = params.get('task_definition')
            
            if not task_definition:
                return {'success': False, 'error': 'No task definition provided'}
            
            # Create task
            task_id = self.task_manager.create_task(
                name=task_definition.get('name', f"Automation_{execution.execution_id}_Task"),
                description=task_definition.get('description', ''),
                task_type=task_definition.get('task_type', 'automation'),
                steps=task_definition.get('steps', []),
                priority=task_definition.get('priority', 'normal')
            )
            
            if not task_id:
                return {'success': False, 'error': 'Failed to create task'}
            
            # Execute task (simplified)
            await asyncio.sleep(0.1)  # Simulate execution
            
            return {
                'success': True,
                'task_id': task_id,
                'type': 'task'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'type': 'task'}
    
    async def _execute_command_action(self, params: Dict[str, Any], 
                                    execution: AutomationExecution) -> Dict[str, Any]:
        """Execute system command action"""
        try:
            command = params.get('command')
            working_dir = params.get('working_dir')
            
            if not command:
                return {'success': False, 'error': 'No command provided'}
            
            # Use terminal manager to execute command
            from ..system.terminal_manager import get_terminal_manager
            terminal_manager = get_terminal_manager()
            
            command_id = terminal_manager.execute_command(
                command=command,
                working_dir=working_dir,
                force_execution=params.get('force_execution', False)
            )
            
            if not command_id:
                return {'success': False, 'error': 'Command execution blocked or failed'}
            
            # Wait for command completion (simplified)
            await asyncio.sleep(1)
            
            return {
                'success': True,
                'command_id': command_id,
                'type': 'system_command'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'type': 'system_command'}
    
    async def _execute_notification_action(self, params: Dict[str, Any], 
                                         execution: AutomationExecution) -> Dict[str, Any]:
        """Execute notification action"""
        try:
            message = params.get('message', 'Automation notification')
            notification_type = params.get('type', 'info')
            
            # Log notification (in real implementation would send actual notification)
            logger.info(f"📢 Automation notification ({notification_type}): {message}")
            
            return {
                'success': True,
                'message': message,
                'type': 'notification'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'type': 'notification'}
    
    async def _execute_custom_action(self, params: Dict[str, Any], 
                                   execution: AutomationExecution) -> Dict[str, Any]:
        """Execute custom action"""
        try:
            action_name = params.get('action_name')
            action_params = params.get('action_params', {})
            
            # Custom action execution logic would go here
            # For now, just simulate success
            await asyncio.sleep(0.1)
            
            return {
                'success': True,
                'action_name': action_name,
                'type': 'custom'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'type': 'custom'}
    
    def _check_resource_availability(self, rule: AutomationRule) -> bool:
        """Check if required resources are available"""
        try:
            required_resources = rule.resource_requirements
            
            for resource_type_str, required_amount in required_resources.items():
                try:
                    resource_type = ResourceType(resource_type_str)
                    available = self.available_resources.get(resource_type, 0.0)
                    
                    # Calculate currently allocated amount
                    allocated = sum(
                        allocation.get(resource_type, 0.0) 
                        for allocation in self.allocated_resources.values()
                    )
                    
                    if available - allocated < required_amount:
                        return False
                        
                except ValueError:
                    # Unknown resource type
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking resource availability: {e}")
            return False
    
    def _allocate_resources(self, execution_id: str, rule: AutomationRule) -> Dict[str, float]:
        """Allocate resources for automation execution"""
        try:
            allocated = {}
            
            for resource_type_str, required_amount in rule.resource_requirements.items():
                try:
                    resource_type = ResourceType(resource_type_str)
                    allocated[resource_type] = required_amount
                except ValueError:
                    continue
            
            if allocated:
                self.allocated_resources[execution_id] = allocated
                logger.debug(f"🤖 Allocated resources for {execution_id}: {allocated}")
            
            return {rt.value: amount for rt, amount in allocated.items()}
            
        except Exception as e:
            logger.error(f"❌ Error allocating resources: {e}")
            return {}
    
    def _deallocate_resources(self, execution_id: str):
        """Deallocate resources after execution completion"""
        try:
            if execution_id in self.allocated_resources:
                deallocated = self.allocated_resources.pop(execution_id)
                logger.debug(f"🤖 Deallocated resources for {execution_id}: {deallocated}")
        except Exception as e:
            logger.error(f"❌ Error deallocating resources: {e}")
    
    def _complete_automation_execution(self, execution: AutomationExecution, success: bool):
        """Complete automation execution"""
        try:
            execution.end_time = datetime.now()
            execution.status = "completed" if success else "failed"
            
            # Calculate execution time
            execution_time = (execution.end_time - execution.start_time).total_seconds()
            execution.performance_metrics['execution_time'] = execution_time
            
            # Deallocate resources
            self._deallocate_resources(execution.execution_id)
            
            # Update statistics
            self.automation_stats['total_executions'] += 1
            if success:
                self.automation_stats['successful_executions'] += 1
            else:
                self.automation_stats['failed_executions'] += 1
            
            # Update average execution time
            total_executions = self.automation_stats['total_executions']
            current_avg = self.automation_stats['average_execution_time']
            new_avg = ((current_avg * (total_executions - 1)) + execution_time) / total_executions
            self.automation_stats['average_execution_time'] = new_avg
            
            # Update success rate
            self.automation_stats['automation_success_rate'] = (
                self.automation_stats['successful_executions'] / total_executions
            )
            
            # Move to history
            self.execution_history.append(execution)
            if len(self.execution_history) > 1000:  # Keep last 1000 executions
                self.execution_history.pop(0)
            
            # Remove from active executions
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
            
            # Emit completion signal
            if success:
                self.automation_completed.emit(execution.execution_id, {
                    'rule_id': execution.rule.rule_id,
                    'execution_time': execution_time,
                    'success_rate': execution.performance_metrics.get('success_rate', 0.0),
                    'results_count': len(execution.results)
                })
            else:
                error_summary = '; '.join(execution.errors[:3]) if execution.errors else 'Unknown error'
                self.automation_failed.emit(execution.execution_id, error_summary)
            
            # Apply optimization if enabled
            if self.optimization_enabled and success:
                asyncio.create_task(self._optimize_automation_rule(execution))
            
            logger.info(f"🤖 Automation execution completed: {execution.execution_id} "
                       f"(Status: {execution.status}, Time: {execution_time:.2f}s)")
            
        except Exception as e:
            logger.error(f"❌ Error completing automation execution: {e}")
    
    async def _optimize_automation_rule(self, execution: AutomationExecution):
        """Optimize automation rule based on execution results"""
        try:
            # Analyze performance
            performance_metrics = execution.performance_metrics
            
            if performance_metrics.get('success_rate', 0.0) > 0.9:
                # High success rate - could optimize for speed or cost
                optimization_suggestions = [
                    "Consider reducing resource allocation",
                    "Optimize action sequence for better performance",
                    "Implement parallel execution where possible"
                ]
            else:
                # Lower success rate - focus on reliability
                optimization_suggestions = [
                    "Add error handling and retry logic",
                    "Increase resource allocation",
                    "Implement better validation checks"
                ]
            
            # Emit optimization signal
            self.optimization_applied.emit(execution.rule.rule_id, {
                'suggestions': optimization_suggestions,
                'performance_metrics': performance_metrics,
                'optimization_type': 'post_execution_analysis'
            })
            
        except Exception as e:
            logger.error(f"❌ Error optimizing automation rule: {e}")
    
    def _process_scheduled_automations(self):
        """Process scheduled automations"""
        try:
            current_time = datetime.now()
            
            for rule_id, rule in self.automation_rules.items():
                if not rule.enabled:
                    continue
                
                schedule = rule.schedule
                schedule_type = schedule.get('type', 'immediate')
                
                if schedule_type == 'recurring':
                    # Check if it's time for recurring execution
                    interval = schedule.get('interval_seconds', 3600)
                    last_execution = self._get_last_execution_time(rule_id)
                    
                    if not last_execution or (current_time - last_execution).total_seconds() >= interval:
                        asyncio.create_task(self.trigger_automation(rule_id, {
                            'triggered_by': 'scheduler',
                            'reason': 'recurring_schedule'
                        }))
                
                elif schedule_type == 'delayed':
                    # Check if delay period has passed
                    delay_until = schedule.get('delay_until')
                    if delay_until and current_time >= datetime.fromisoformat(delay_until):
                        asyncio.create_task(self.trigger_automation(rule_id, {
                            'triggered_by': 'scheduler',
                            'reason': 'delayed_schedule'
                        }))
                        
                        # Remove delay to prevent re-triggering
                        schedule.pop('delay_until', None)
                
        except Exception as e:
            logger.error(f"❌ Error processing scheduled automations: {e}")
    
    def _monitor_automations(self):
        """Monitor active automations"""
        try:
            current_time = datetime.now()
            
            for execution_id, execution in list(self.active_executions.items()):
                # Check for timeout
                max_execution_time = execution.rule.metadata.get('max_execution_time', 3600)
                elapsed_time = (current_time - execution.start_time).total_seconds()
                
                if elapsed_time > max_execution_time:
                    logger.warning(f"⚠️ Automation execution timeout: {execution_id}")
                    execution.status = "timeout"
                    execution.errors.append("Execution timeout")
                    self._complete_automation_execution(execution, False)
            
        except Exception as e:
            logger.error(f"❌ Error monitoring automations: {e}")
    
    def _validate_automation_rule(self, rule: AutomationRule) -> bool:
        """Validate automation rule"""
        try:
            # Basic validation
            if not rule.name or not rule.actions:
                return False
            
            # Validate actions
            for action in rule.actions:
                if 'type' not in action:
                    return False
            
            # Validate trigger conditions
            if not rule.trigger_conditions:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating automation rule: {e}")
            return False
    
    def _get_last_execution_time(self, rule_id: str) -> Optional[datetime]:
        """Get last execution time for a rule"""
        for execution in reversed(self.execution_history):
            if execution.rule.rule_id == rule_id:
                return execution.start_time
        return None
    
    def _generate_rule_id(self) -> str:
        """Generate unique rule ID"""
        self.rule_counter += 1
        return f"rule_{self.rule_counter:06d}"
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        self.execution_counter += 1
        return f"exec_{self.execution_counter:06d}"
    
    def get_automation_rules(self) -> List[Dict[str, Any]]:
        """Get all automation rules"""
        return [self._rule_to_dict(rule) for rule in self.automation_rules.values()]
    
    def get_active_executions(self) -> List[Dict[str, Any]]:
        """Get active executions"""
        return [self._execution_to_dict(execution) for execution in self.active_executions.values()]
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history"""
        history = self.execution_history[-limit:] if limit > 0 else self.execution_history
        return [self._execution_to_dict(execution) for execution in history]
    
    def get_automation_stats(self) -> Dict[str, Any]:
        """Get automation statistics"""
        return self.automation_stats.copy()
    
    def _rule_to_dict(self, rule: AutomationRule) -> Dict[str, Any]:
        """Convert AutomationRule to dictionary"""
        return {
            'rule_id': rule.rule_id,
            'name': rule.name,
            'description': rule.description,
            'enabled': rule.enabled,
            'priority': rule.priority,
            'actions_count': len(rule.actions),
            'schedule_type': rule.schedule.get('type', 'immediate'),
            'metadata': rule.metadata
        }
    
    def _execution_to_dict(self, execution: AutomationExecution) -> Dict[str, Any]:
        """Convert AutomationExecution to dictionary"""
        return {
            'execution_id': execution.execution_id,
            'rule_id': execution.rule.rule_id,
            'rule_name': execution.rule.name,
            'status': execution.status,
            'start_time': execution.start_time.isoformat(),
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'triggered_by': execution.triggered_by,
            'results_count': len(execution.results),
            'errors_count': len(execution.errors),
            'performance_metrics': execution.performance_metrics
        }

# Singleton instance
_automation_controller = None

def get_automation_controller() -> AutomationController:
    """Get the singleton Automation Controller instance"""
    global _automation_controller
    if _automation_controller is None:
        _automation_controller = AutomationController()
    return _automation_controller
