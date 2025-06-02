"""
Workflow Builder for Orion Vision Core

This module provides workflow construction and validation utilities.
Extracted from task_orchestration.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict

from .workflow_engine import WorkflowDefinition, WorkflowStep
from ..core.task_base import TaskDefinition, TaskPriority
from ...agent.core.agent_logger import AgentLogger


class WorkflowBuilder:
    """
    Workflow Builder
    
    Provides fluent API for building complex workflows with validation.
    """
    
    def __init__(self, logger: Optional[AgentLogger] = None):
        """Initialize workflow builder"""
        self.logger = logger or AgentLogger("workflow_builder")
        
        # Current workflow being built
        self.current_workflow: Optional[WorkflowDefinition] = None
        self.step_counter = 0
        
        # Builder state
        self.validation_errors: List[str] = []
        
        self.logger.info("Workflow Builder initialized")
    
    def create_workflow(self, name: str, description: str = "", version: str = "1.0.0") -> 'WorkflowBuilder':
        """Create new workflow"""
        self.current_workflow = WorkflowDefinition(
            workflow_name=name,
            description=description,
            version=version
        )
        self.step_counter = 0
        self.validation_errors.clear()
        
        self.logger.info(
            "New workflow created",
            workflow_name=name,
            version=version
        )
        
        return self
    
    def add_task_step(self, 
                     step_name: str,
                     task_name: str,
                     task_type: str,
                     input_data: Dict[str, Any] = None,
                     required_capabilities: List[str] = None,
                     priority: TaskPriority = TaskPriority.NORMAL,
                     timeout: float = 300.0,
                     depends_on: List[str] = None,
                     condition: str = None,
                     max_retries: int = 3) -> 'WorkflowBuilder':
        """Add task step to workflow"""
        if not self.current_workflow:
            raise ValueError("No workflow created. Call create_workflow() first.")
        
        # Create task definition
        task_def = TaskDefinition(
            task_name=task_name,
            task_type=task_type,
            input_data=input_data or {},
            required_capabilities=required_capabilities or [],
            priority=priority,
            timeout=timeout
        )
        
        # Create workflow step
        step = WorkflowStep(
            step_name=step_name,
            step_type="task",
            task_definition=task_def,
            depends_on=depends_on or [],
            condition=condition,
            max_retries=max_retries
        )
        
        self.current_workflow.add_step(step)
        self.step_counter += 1
        
        self.logger.info(
            "Task step added to workflow",
            step_name=step_name,
            task_name=task_name,
            task_type=task_type,
            dependencies=len(depends_on or [])
        )
        
        return self
    
    def add_decision_step(self,
                         step_name: str,
                         condition: str,
                         true_steps: List[str] = None,
                         false_steps: List[str] = None,
                         depends_on: List[str] = None) -> 'WorkflowBuilder':
        """Add decision step to workflow"""
        if not self.current_workflow:
            raise ValueError("No workflow created. Call create_workflow() first.")
        
        # Create decision step
        step = WorkflowStep(
            step_name=step_name,
            step_type="decision",
            depends_on=depends_on or [],
            condition=condition,
            metadata={
                'true_steps': true_steps or [],
                'false_steps': false_steps or []
            }
        )
        
        self.current_workflow.add_step(step)
        self.step_counter += 1
        
        self.logger.info(
            "Decision step added to workflow",
            step_name=step_name,
            condition=condition,
            true_steps_count=len(true_steps or []),
            false_steps_count=len(false_steps or [])
        )
        
        return self
    
    def add_parallel_group(self,
                          group_name: str,
                          parallel_steps: List[Dict[str, Any]],
                          depends_on: List[str] = None,
                          wait_for_all: bool = True) -> 'WorkflowBuilder':
        """Add parallel execution group"""
        if not self.current_workflow:
            raise ValueError("No workflow created. Call create_workflow() first.")
        
        # Create parallel steps
        group_step_ids = []
        
        for step_config in parallel_steps:
            step_name = f"{group_name}_{step_config.get('name', f'step_{len(group_step_ids) + 1}')}"
            
            if step_config.get('type') == 'task':
                self.add_task_step(
                    step_name=step_name,
                    task_name=step_config.get('task_name', step_name),
                    task_type=step_config.get('task_type', 'generic'),
                    input_data=step_config.get('input_data', {}),
                    required_capabilities=step_config.get('required_capabilities', []),
                    priority=step_config.get('priority', TaskPriority.NORMAL),
                    timeout=step_config.get('timeout', 300.0),
                    depends_on=depends_on,  # All parallel steps depend on same prerequisites
                    max_retries=step_config.get('max_retries', 3)
                )
                group_step_ids.append(self.current_workflow.steps[-1].step_id)
        
        # Create group metadata step
        group_step = WorkflowStep(
            step_name=f"{group_name}_group",
            step_type="parallel_group",
            depends_on=group_step_ids if wait_for_all else [],
            metadata={
                'group_name': group_name,
                'parallel_steps': group_step_ids,
                'wait_for_all': wait_for_all
            }
        )
        
        self.current_workflow.add_step(group_step)
        self.step_counter += 1
        
        self.logger.info(
            "Parallel group added to workflow",
            group_name=group_name,
            parallel_steps_count=len(parallel_steps),
            wait_for_all=wait_for_all
        )
        
        return self
    
    def set_workflow_config(self,
                           timeout: float = None,
                           max_parallel_steps: int = None,
                           failure_strategy: str = None,
                           metadata: Dict[str, Any] = None,
                           tags: List[str] = None) -> 'WorkflowBuilder':
        """Set workflow configuration"""
        if not self.current_workflow:
            raise ValueError("No workflow created. Call create_workflow() first.")
        
        if timeout is not None:
            self.current_workflow.timeout = timeout
        if max_parallel_steps is not None:
            self.current_workflow.max_parallel_steps = max_parallel_steps
        if failure_strategy is not None:
            self.current_workflow.failure_strategy = failure_strategy
        if metadata is not None:
            self.current_workflow.metadata.update(metadata)
        if tags is not None:
            self.current_workflow.tags.extend(tags)
        
        self.logger.info(
            "Workflow configuration updated",
            timeout=self.current_workflow.timeout,
            max_parallel_steps=self.current_workflow.max_parallel_steps,
            failure_strategy=self.current_workflow.failure_strategy
        )
        
        return self
    
    def validate_workflow(self) -> bool:
        """Validate current workflow"""
        if not self.current_workflow:
            self.validation_errors.append("No workflow created")
            return False
        
        self.validation_errors.clear()
        
        try:
            # Basic validation
            self.current_workflow.__post_init__()
            
            # Dependency validation
            if not self.current_workflow.validate_dependencies():
                self.validation_errors.append("Invalid step dependencies")
            
            # Step validation
            for step in self.current_workflow.steps:
                try:
                    step.__post_init__()
                except ValueError as e:
                    self.validation_errors.append(f"Step {step.step_name}: {e}")
            
            # Circular dependency check
            if self._has_circular_dependencies():
                self.validation_errors.append("Circular dependencies detected")
            
            # Orphaned steps check
            orphaned_steps = self._find_orphaned_steps()
            if orphaned_steps:
                self.validation_errors.append(f"Orphaned steps found: {orphaned_steps}")
            
            is_valid = len(self.validation_errors) == 0
            
            self.logger.info(
                "Workflow validation completed",
                workflow_name=self.current_workflow.workflow_name,
                is_valid=is_valid,
                errors_count=len(self.validation_errors)
            )
            
            if not is_valid:
                for error in self.validation_errors:
                    self.logger.warning("Validation error", error=error)
            
            return is_valid
            
        except Exception as e:
            self.validation_errors.append(f"Validation error: {e}")
            self.logger.error("Workflow validation failed", error=str(e))
            return False
    
    def build(self) -> Optional[WorkflowDefinition]:
        """Build and return workflow definition"""
        if not self.validate_workflow():
            self.logger.error(
                "Cannot build workflow - validation failed",
                errors=self.validation_errors
            )
            return None
        
        workflow = self.current_workflow
        self.current_workflow = None
        self.step_counter = 0
        
        self.logger.info(
            "Workflow built successfully",
            workflow_name=workflow.workflow_name,
            steps_count=len(workflow.steps)
        )
        
        return workflow
    
    def to_json(self) -> Optional[str]:
        """Export workflow to JSON"""
        if not self.current_workflow:
            return None
        
        try:
            workflow_dict = asdict(self.current_workflow)
            return json.dumps(workflow_dict, indent=2, default=str)
        except Exception as e:
            self.logger.error("Failed to export workflow to JSON", error=str(e))
            return None
    
    def from_json(self, json_str: str) -> 'WorkflowBuilder':
        """Import workflow from JSON"""
        try:
            workflow_dict = json.loads(json_str)
            
            # Create workflow
            self.create_workflow(
                name=workflow_dict.get('workflow_name', 'Imported Workflow'),
                description=workflow_dict.get('description', ''),
                version=workflow_dict.get('version', '1.0.0')
            )
            
            # Set configuration
            self.current_workflow.timeout = workflow_dict.get('timeout', 3600.0)
            self.current_workflow.max_parallel_steps = workflow_dict.get('max_parallel_steps', 5)
            self.current_workflow.failure_strategy = workflow_dict.get('failure_strategy', 'stop')
            self.current_workflow.metadata = workflow_dict.get('metadata', {})
            self.current_workflow.tags = workflow_dict.get('tags', [])
            
            # Add steps
            for step_dict in workflow_dict.get('steps', []):
                step = WorkflowStep(
                    step_id=step_dict.get('step_id'),
                    step_name=step_dict.get('step_name'),
                    step_type=step_dict.get('step_type'),
                    depends_on=step_dict.get('depends_on', []),
                    condition=step_dict.get('condition'),
                    max_retries=step_dict.get('max_retries', 3),
                    metadata=step_dict.get('metadata', {})
                )
                
                # Add task definition if present
                if step_dict.get('task_definition'):
                    task_dict = step_dict['task_definition']
                    step.task_definition = TaskDefinition(
                        task_id=task_dict.get('task_id'),
                        task_name=task_dict.get('task_name'),
                        task_type=task_dict.get('task_type'),
                        input_data=task_dict.get('input_data', {}),
                        required_capabilities=task_dict.get('required_capabilities', []),
                        timeout=task_dict.get('timeout', 300.0)
                    )
                
                self.current_workflow.add_step(step)
            
            self.logger.info(
                "Workflow imported from JSON",
                workflow_name=self.current_workflow.workflow_name,
                steps_count=len(self.current_workflow.steps)
            )
            
        except Exception as e:
            self.logger.error("Failed to import workflow from JSON", error=str(e))
            raise
        
        return self
    
    def _has_circular_dependencies(self) -> bool:
        """Check for circular dependencies"""
        if not self.current_workflow:
            return False
        
        # Build adjacency list
        graph = {}
        for step in self.current_workflow.steps:
            graph[step.step_id] = step.depends_on.copy()
        
        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_id in graph:
            if step_id not in visited:
                if has_cycle(step_id):
                    return True
        
        return False
    
    def _find_orphaned_steps(self) -> List[str]:
        """Find steps that are not reachable"""
        if not self.current_workflow:
            return []
        
        # Find root steps (no dependencies)
        root_steps = []
        all_steps = set()
        
        for step in self.current_workflow.steps:
            all_steps.add(step.step_id)
            if not step.depends_on:
                root_steps.append(step.step_id)
        
        # BFS from root steps
        reachable = set()
        queue = root_steps.copy()
        
        while queue:
            current = queue.pop(0)
            if current in reachable:
                continue
            
            reachable.add(current)
            
            # Find steps that depend on current
            for step in self.current_workflow.steps:
                if current in step.depends_on and step.step_id not in reachable:
                    queue.append(step.step_id)
        
        # Find orphaned steps
        orphaned = all_steps - reachable
        return list(orphaned)
    
    def get_validation_errors(self) -> List[str]:
        """Get current validation errors"""
        return self.validation_errors.copy()
    
    def get_current_workflow_info(self) -> Optional[Dict[str, Any]]:
        """Get current workflow information"""
        if not self.current_workflow:
            return None
        
        return {
            'workflow_name': self.current_workflow.workflow_name,
            'description': self.current_workflow.description,
            'version': self.current_workflow.version,
            'steps_count': len(self.current_workflow.steps),
            'timeout': self.current_workflow.timeout,
            'max_parallel_steps': self.current_workflow.max_parallel_steps,
            'failure_strategy': self.current_workflow.failure_strategy,
            'tags': self.current_workflow.tags
        }
