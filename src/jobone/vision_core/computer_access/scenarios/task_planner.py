#!/usr/bin/env python3
"""
Task Planner - Intelligent task planning and sequencing
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from . import scenarios_metrics

class TaskType(Enum):
    """Types of tasks"""
    TERMINAL = "terminal"
    GUI = "gui"
    FILE_OPERATION = "file_operation"
    NETWORK = "network"
    SYSTEM = "system"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Individual task definition"""
    task_id: str
    task_type: TaskType
    action: str
    parameters: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = None
    estimated_duration: float = 30.0
    timeout: float = 60.0

@dataclass
class TaskPlan:
    """Complete task execution plan"""
    plan_id: str
    tasks: List[Task]
    total_estimated_duration: float
    dependencies_resolved: bool
    optimization_applied: bool

class TaskPlanner:
    """
    Intelligent task planning and sequencing
    Optimizes task execution order and resolves dependencies
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.computer_access.scenarios.planner')
        
        # Planning state
        self.initialized = False
        self.active_plans = {}
        self.completed_plans = {}
        
        # Planning algorithms
        self.optimization_enabled = True
        self.dependency_resolution_enabled = True
        
        # Performance tracking
        self.plans_created = 0
        self.successful_plans = 0
        self.failed_plans = 0
        self.total_planning_time = 0.0
        
        # Task templates
        self.task_templates = {}
        
        self.logger.info("📋 TaskPlanner initialized")
    
    def initialize(self) -> bool:
        """
        Initialize task planner
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing task planner...")
            
            # Load task templates
            self._load_task_templates()
            
            self.initialized = True
            self.logger.info("✅ Task planner initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Task planner initialization failed: {e}")
            return False
    
    def create_plan(self, goal: str, parameters: Dict[str, Any]) -> TaskPlan:
        """
        Create task execution plan for a goal
        
        Args:
            goal: High-level goal description
            parameters: Goal parameters
            
        Returns:
            TaskPlan: Generated task plan
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"📋 Creating plan for goal: {goal}")
            
            # Generate tasks based on goal
            tasks = self._generate_tasks(goal, parameters)
            
            # Resolve dependencies
            if self.dependency_resolution_enabled:
                tasks = self._resolve_dependencies(tasks)
            
            # Optimize task order
            if self.optimization_enabled:
                tasks = self._optimize_task_order(tasks)
            
            # Calculate total estimated duration
            total_duration = sum(task.estimated_duration for task in tasks)
            
            # Create plan
            plan_id = f"plan_{int(time.time())}"
            plan = TaskPlan(
                plan_id=plan_id,
                tasks=tasks,
                total_estimated_duration=total_duration,
                dependencies_resolved=self.dependency_resolution_enabled,
                optimization_applied=self.optimization_enabled
            )
            
            # Store plan
            self.active_plans[plan_id] = plan
            self.plans_created += 1
            
            planning_time = time.time() - start_time
            self.total_planning_time += planning_time
            scenarios_metrics.record_planning_time(planning_time)
            
            self.logger.info(f"✅ Plan created: {len(tasks)} tasks, {total_duration:.1f}s estimated ({planning_time:.3f}s)")
            
            return plan
            
        except Exception as e:
            planning_time = time.time() - start_time
            self.total_planning_time += planning_time
            
            self.logger.error(f"❌ Plan creation failed: {e}")
            raise
    
    def _generate_tasks(self, goal: str, parameters: Dict[str, Any]) -> List[Task]:
        """Generate tasks based on goal"""
        tasks = []
        
        # Simple goal-to-task mapping
        if goal == "create_text_file":
            filename = parameters.get('filename', 'test.txt')
            content = parameters.get('content', 'Hello World')
            
            tasks.append(Task(
                task_id="create_file",
                task_type=TaskType.TERMINAL,
                action="create_file",
                parameters={'filename': filename, 'content': content},
                estimated_duration=5.0
            ))
            
            tasks.append(Task(
                task_id="verify_file",
                task_type=TaskType.TERMINAL,
                action="read_file",
                parameters={'filename': filename},
                dependencies=["create_file"],
                estimated_duration=3.0
            ))
        
        elif goal == "open_text_editor":
            editor = parameters.get('editor', 'notepad')
            
            tasks.append(Task(
                task_id="find_editor",
                task_type=TaskType.GUI,
                action="find_element",
                parameters={'element': editor},
                estimated_duration=10.0
            ))
            
            tasks.append(Task(
                task_id="open_editor",
                task_type=TaskType.GUI,
                action="click",
                parameters={'target': editor},
                dependencies=["find_editor"],
                estimated_duration=5.0
            ))
        
        elif goal == "type_and_save":
            text = parameters.get('text', 'Sample text')
            
            tasks.append(Task(
                task_id="type_text",
                task_type=TaskType.GUI,
                action="type_text",
                parameters={'text': text},
                estimated_duration=len(text) * 0.1  # Estimate based on text length
            ))
            
            tasks.append(Task(
                task_id="save_document",
                task_type=TaskType.GUI,
                action="shortcut",
                parameters={'shortcut_name': 'save'},
                dependencies=["type_text"],
                estimated_duration=3.0
            ))
        
        elif goal == "file_operations":
            source_file = parameters.get('source_file', 'source.txt')
            target_file = parameters.get('target_file', 'target.txt')
            
            tasks.append(Task(
                task_id="create_source",
                task_type=TaskType.TERMINAL,
                action="create_file",
                parameters={'filename': source_file, 'content': 'Source content'},
                estimated_duration=5.0
            ))
            
            tasks.append(Task(
                task_id="copy_file",
                task_type=TaskType.TERMINAL,
                action="execute_command",
                parameters={'command': f'cp {source_file} {target_file}'},
                dependencies=["create_source"],
                estimated_duration=3.0
            ))
            
            tasks.append(Task(
                task_id="verify_copy",
                task_type=TaskType.TERMINAL,
                action="read_file",
                parameters={'filename': target_file},
                dependencies=["copy_file"],
                estimated_duration=3.0
            ))
        
        else:
            # Generic task creation
            tasks.append(Task(
                task_id="generic_task",
                task_type=TaskType.TERMINAL,
                action="execute_command",
                parameters=parameters,
                estimated_duration=30.0
            ))
        
        return tasks
    
    def _resolve_dependencies(self, tasks: List[Task]) -> List[Task]:
        """Resolve task dependencies and order tasks"""
        self.logger.debug("🔗 Resolving task dependencies...")
        
        # Create dependency graph
        task_map = {task.task_id: task for task in tasks}
        resolved_tasks = []
        remaining_tasks = tasks.copy()
        
        # Iteratively resolve dependencies
        max_iterations = len(tasks) * 2  # Prevent infinite loops
        iteration = 0
        
        while remaining_tasks and iteration < max_iterations:
            iteration += 1
            progress_made = False
            
            for task in remaining_tasks.copy():
                # Check if all dependencies are resolved
                if not task.dependencies:
                    # No dependencies, can be added
                    resolved_tasks.append(task)
                    remaining_tasks.remove(task)
                    progress_made = True
                else:
                    # Check if all dependencies are in resolved_tasks
                    resolved_ids = [t.task_id for t in resolved_tasks]
                    if all(dep in resolved_ids for dep in task.dependencies):
                        resolved_tasks.append(task)
                        remaining_tasks.remove(task)
                        progress_made = True
            
            if not progress_made:
                # Circular dependency or missing dependency
                self.logger.warning("⚠️ Circular or missing dependencies detected")
                # Add remaining tasks anyway
                resolved_tasks.extend(remaining_tasks)
                break
        
        self.logger.debug(f"🔗 Dependencies resolved: {len(resolved_tasks)} tasks ordered")
        return resolved_tasks
    
    def _optimize_task_order(self, tasks: List[Task]) -> List[Task]:
        """Optimize task execution order"""
        self.logger.debug("⚡ Optimizing task order...")
        
        # Simple optimization: group by task type and priority
        terminal_tasks = [t for t in tasks if t.task_type == TaskType.TERMINAL]
        gui_tasks = [t for t in tasks if t.task_type == TaskType.GUI]
        other_tasks = [t for t in tasks if t.task_type not in [TaskType.TERMINAL, TaskType.GUI]]
        
        # Sort each group by priority
        terminal_tasks.sort(key=lambda t: t.priority.value, reverse=True)
        gui_tasks.sort(key=lambda t: t.priority.value, reverse=True)
        other_tasks.sort(key=lambda t: t.priority.value, reverse=True)
        
        # Interleave tasks to minimize context switching
        optimized_tasks = []
        max_len = max(len(terminal_tasks), len(gui_tasks), len(other_tasks))
        
        for i in range(max_len):
            if i < len(terminal_tasks):
                optimized_tasks.append(terminal_tasks[i])
            if i < len(gui_tasks):
                optimized_tasks.append(gui_tasks[i])
            if i < len(other_tasks):
                optimized_tasks.append(other_tasks[i])
        
        self.logger.debug(f"⚡ Task order optimized: {len(optimized_tasks)} tasks")
        return optimized_tasks
    
    def _load_task_templates(self):
        """Load predefined task templates"""
        self.task_templates = {
            'file_creation': {
                'type': TaskType.TERMINAL,
                'action': 'create_file',
                'estimated_duration': 5.0
            },
            'text_input': {
                'type': TaskType.GUI,
                'action': 'type_text',
                'estimated_duration': 10.0
            },
            'button_click': {
                'type': TaskType.GUI,
                'action': 'click',
                'estimated_duration': 2.0
            },
            'file_copy': {
                'type': TaskType.TERMINAL,
                'action': 'execute_command',
                'estimated_duration': 3.0
            }
        }
    
    def get_plan(self, plan_id: str) -> Optional[TaskPlan]:
        """Get plan by ID"""
        return self.active_plans.get(plan_id) or self.completed_plans.get(plan_id)
    
    def update_plan_status(self, plan_id: str, completed: bool):
        """Update plan completion status"""
        if plan_id in self.active_plans:
            plan = self.active_plans.pop(plan_id)
            self.completed_plans[plan_id] = plan
            
            if completed:
                self.successful_plans += 1
            else:
                self.failed_plans += 1
    
    def estimate_duration(self, tasks: List[Task]) -> float:
        """Estimate total duration for tasks"""
        return sum(task.estimated_duration for task in tasks)
    
    def validate_plan(self, plan: TaskPlan) -> Tuple[bool, List[str]]:
        """Validate task plan"""
        issues = []
        
        # Check for circular dependencies
        task_ids = [task.task_id for task in plan.tasks]
        for task in plan.tasks:
            if task.dependencies:
                for dep in task.dependencies:
                    if dep not in task_ids:
                        issues.append(f"Task {task.task_id} has missing dependency: {dep}")
        
        # Check for reasonable durations
        for task in plan.tasks:
            if task.estimated_duration <= 0:
                issues.append(f"Task {task.task_id} has invalid duration: {task.estimated_duration}")
            if task.timeout <= task.estimated_duration:
                issues.append(f"Task {task.task_id} timeout too short for estimated duration")
        
        return len(issues) == 0, issues
    
    def is_ready(self) -> bool:
        """Check if task planner is ready"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get task planner status"""
        avg_planning_time = self.total_planning_time / max(self.plans_created, 1)
        
        return {
            'initialized': self.initialized,
            'plans_created': self.plans_created,
            'successful_plans': self.successful_plans,
            'failed_plans': self.failed_plans,
            'success_rate': (self.successful_plans / max(self.plans_created, 1)) * 100,
            'active_plans': len(self.active_plans),
            'completed_plans': len(self.completed_plans),
            'total_planning_time': self.total_planning_time,
            'average_planning_time': avg_planning_time,
            'optimization_enabled': self.optimization_enabled,
            'dependency_resolution_enabled': self.dependency_resolution_enabled,
            'task_templates_loaded': len(self.task_templates)
        }
    
    def shutdown(self):
        """Shutdown task planner"""
        self.logger.info("🛑 Shutting down task planner")
        
        # Clear active plans
        self.active_plans.clear()
        
        self.initialized = False
        self.logger.info("✅ Task planner shutdown complete")
