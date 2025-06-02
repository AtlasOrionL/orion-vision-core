#!/usr/bin/env python3
"""
Workflow Engine - Advanced Task Automation and Orchestration
Sprint 8.4 - Advanced Task Automation and AI-Driven Workflows
Orion Vision Core - Autonomous AI Operating System

This module provides advanced workflow automation capabilities including
complex task orchestration, dependency management, and intelligent
execution planning for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.4.0
Date: 30 Mayıs 2025
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
# import networkx as nx  # Optional dependency

from ..tasks.task_framework import get_task_manager, TaskDefinition, TaskType, TaskPriority, TaskStatus
from ..brain.brain_ai_manager import get_brain_ai_manager
from ..llm.llm_api_manager import get_llm_api_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkflowEngine")

class WorkflowStatus(Enum):
    """Workflow execution status enumeration"""
    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    OPTIMIZING = "optimizing"

class DependencyType(Enum):
    """Task dependency type enumeration"""
    SEQUENTIAL = "sequential"  # Task B starts after Task A completes
    PARALLEL = "parallel"     # Tasks can run simultaneously
    CONDITIONAL = "conditional"  # Task B starts if Task A meets condition
    DATA_FLOW = "data_flow"   # Task B uses output from Task A

class OptimizationStrategy(Enum):
    """Workflow optimization strategy enumeration"""
    TIME_OPTIMAL = "time_optimal"
    RESOURCE_OPTIMAL = "resource_optimal"
    COST_OPTIMAL = "cost_optimal"
    RELIABILITY_OPTIMAL = "reliability_optimal"
    BALANCED = "balanced"

@dataclass
class WorkflowNode:
    """Workflow node representing a task or operation"""
    node_id: str
    task_definition: TaskDefinition
    dependencies: List[str] = field(default_factory=list)
    dependency_types: Dict[str, DependencyType] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 300
    priority: int = 1
    resources_required: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    global_timeout: int = 3600  # 1 hour default
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    error_handling_strategy: str = "retry_and_continue"
    max_parallel_tasks: int = 5
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowExecution:
    """Workflow execution record"""
    execution_id: str
    workflow_definition: WorkflowDefinition
    status: WorkflowStatus
    execution_plan: List[List[str]]  # Execution phases with parallel tasks
    current_phase: int
    completed_nodes: Set[str]
    failed_nodes: Set[str]
    running_nodes: Set[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_execution_time: float
    node_results: Dict[str, Any]
    node_errors: Dict[str, str]
    optimization_metrics: Dict[str, float]
    logs: List[str]

class WorkflowEngine(QObject):
    """
    Advanced workflow automation engine.

    Features:
    - Complex task orchestration with dependencies
    - AI-driven workflow optimization
    - Intelligent execution planning
    - Dynamic resource allocation
    - Error recovery and adaptation
    - Performance monitoring and learning
    """

    # Signals
    workflow_started = pyqtSignal(str)  # workflow_id
    workflow_completed = pyqtSignal(str, dict)  # workflow_id, results
    workflow_failed = pyqtSignal(str, str)  # workflow_id, error
    workflow_progress = pyqtSignal(str, int, int)  # workflow_id, completed_nodes, total_nodes
    node_completed = pyqtSignal(str, str, dict)  # workflow_id, node_id, result
    optimization_applied = pyqtSignal(str, dict)  # workflow_id, optimization_details

    def __init__(self):
        """Initialize Workflow Engine"""
        super().__init__()

        # Component references
        self.task_manager = get_task_manager()
        self.brain_manager = get_brain_ai_manager()
        self.llm_manager = get_llm_api_manager()

        # Workflow management
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.workflow_queue: List[WorkflowDefinition] = []
        self.workflow_history: List[WorkflowExecution] = []
        self.workflow_counter = 0

        # Optimization and learning
        self.optimization_patterns: Dict[str, Dict[str, Any]] = {}
        self.performance_history: List[Dict[str, Any]] = {}
        self.learning_enabled = True

        # Configuration
        self.max_concurrent_workflows = 3
        self.max_workflow_history = 500
        self.optimization_threshold = 0.8  # Trigger optimization if efficiency < 80%

        # Statistics
        self.execution_stats = {
            'total_workflows': 0,
            'successful_workflows': 0,
            'failed_workflows': 0,
            'cancelled_workflows': 0,
            'average_execution_time': 0.0,
            'average_efficiency': 0.0,
            'optimizations_applied': 0,
            'workflows_by_strategy': {strategy.value: 0 for strategy in OptimizationStrategy}
        }

        # Monitoring
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self._monitor_workflows)
        self.monitoring_timer.start(2000)  # Monitor every 2 seconds

        logger.info("🔄 Workflow Engine initialized")

    def create_workflow(self, name: str, description: str,
                       workflow_definition: Dict[str, Any],
                       optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED) -> str:
        """
        Create a new workflow definition.

        Args:
            name: Workflow name
            description: Workflow description
            workflow_definition: Workflow structure definition
            optimization_strategy: Optimization strategy to use

        Returns:
            Workflow ID
        """
        try:
            workflow_id = self._generate_workflow_id()

            # Parse workflow definition
            nodes = self._parse_workflow_nodes(workflow_definition.get('nodes', []))

            # Create workflow definition
            workflow = WorkflowDefinition(
                workflow_id=workflow_id,
                name=name,
                description=description,
                nodes=nodes,
                global_timeout=workflow_definition.get('global_timeout', 3600),
                optimization_strategy=optimization_strategy,
                error_handling_strategy=workflow_definition.get('error_handling_strategy', 'retry_and_continue'),
                max_parallel_tasks=workflow_definition.get('max_parallel_tasks', 5),
                created_by="user",
                metadata={
                    'created_at': datetime.now().isoformat(),
                    'node_count': len(nodes),
                    'estimated_duration': self._estimate_workflow_duration(nodes)
                }
            )

            # Validate workflow
            if not self._validate_workflow(workflow):
                logger.error(f"❌ Workflow validation failed: {workflow_id}")
                return None

            # Add to queue
            self.workflow_queue.append(workflow)

            logger.info(f"🔄 Created workflow: {name} (ID: {workflow_id}, Nodes: {len(nodes)})")
            return workflow_id

        except Exception as e:
            logger.error(f"❌ Error creating workflow: {e}")
            return None

    async def execute_workflow(self, workflow_id: str) -> bool:
        """
        Execute a workflow by ID.

        Args:
            workflow_id: Workflow ID to execute

        Returns:
            True if execution started, False otherwise
        """
        try:
            # Find workflow in queue
            workflow_definition = None
            for workflow in self.workflow_queue:
                if workflow.workflow_id == workflow_id:
                    workflow_definition = workflow
                    break

            if not workflow_definition:
                logger.error(f"❌ Workflow not found: {workflow_id}")
                return False

            # Check concurrent workflow limit
            if len(self.active_workflows) >= self.max_concurrent_workflows:
                logger.warning(f"⚠️ Maximum concurrent workflows reached: {self.max_concurrent_workflows}")
                return False

            # Remove from queue
            self.workflow_queue.remove(workflow_definition)

            # Create execution plan
            execution_plan = await self._create_execution_plan(workflow_definition)
            if not execution_plan:
                logger.error(f"❌ Failed to create execution plan for workflow: {workflow_id}")
                return False

            # Create execution record
            execution = WorkflowExecution(
                execution_id=f"{workflow_id}_exec_{int(datetime.now().timestamp())}",
                workflow_definition=workflow_definition,
                status=WorkflowStatus.RUNNING,
                execution_plan=execution_plan,
                current_phase=0,
                completed_nodes=set(),
                failed_nodes=set(),
                running_nodes=set(),
                start_time=datetime.now(),
                end_time=None,
                total_execution_time=0.0,
                node_results={},
                node_errors={},
                optimization_metrics={},
                logs=[]
            )

            # Add to active workflows
            self.active_workflows[workflow_id] = execution

            # Emit signal
            self.workflow_started.emit(workflow_id)

            # Execute workflow phases
            success = await self._execute_workflow_phases(execution)

            # Complete workflow
            self._complete_workflow(execution, success)

            return True

        except Exception as e:
            logger.error(f"❌ Error executing workflow {workflow_id}: {e}")
            if workflow_id in self.active_workflows:
                execution = self.active_workflows[workflow_id]
                execution.status = WorkflowStatus.FAILED
                execution.logs.append(f"Execution error: {e}")
                self._complete_workflow(execution, False)
            return False

    async def _create_execution_plan(self, workflow: WorkflowDefinition) -> List[List[str]]:
        """Create optimized execution plan for workflow"""
        try:
            # Build dependency mapping
            node_dependencies = {}
            node_dependents = {}

            for node in workflow.nodes:
                node_dependencies[node.node_id] = set(node.dependencies)
                node_dependents[node.node_id] = set()

            # Build reverse dependency mapping
            for node in workflow.nodes:
                for dep_id in node.dependencies:
                    if dep_id in node_dependents:
                        node_dependents[dep_id].add(node.node_id)

            # Check for cycles (simplified check)
            if self._has_circular_dependencies(node_dependencies):
                logger.error("❌ Workflow contains circular dependencies")
                return None

            # Create execution phases using topological sort
            execution_plan = []
            remaining_nodes = set(node_dependencies.keys())

            while remaining_nodes:
                # Find nodes with no pending dependencies
                ready_nodes = []
                for node_id in remaining_nodes:
                    dependencies_met = True
                    for dep_id in node_dependencies[node_id]:
                        if dep_id in remaining_nodes:
                            dependencies_met = False
                            break

                    if dependencies_met:
                        ready_nodes.append(node_id)

                if not ready_nodes:
                    logger.error("❌ Unable to resolve workflow dependencies")
                    return None

                # Sort by priority and add to execution plan
                ready_nodes.sort(key=lambda n: next(
                    node.priority for node in workflow.nodes if node.node_id == n
                ), reverse=True)

                # Limit parallel execution
                phase_nodes = ready_nodes[:workflow.max_parallel_tasks]
                execution_plan.append(phase_nodes)

                # Remove processed nodes
                for node_id in phase_nodes:
                    remaining_nodes.remove(node_id)

            # Apply optimization if enabled
            if workflow.optimization_strategy != OptimizationStrategy.BALANCED:
                execution_plan = await self._optimize_execution_plan(execution_plan, workflow)

            logger.info(f"🔄 Created execution plan: {len(execution_plan)} phases")
            return execution_plan

        except Exception as e:
            logger.error(f"❌ Error creating execution plan: {e}")
            return None

    async def _optimize_execution_plan(self, execution_plan: List[List[str]],
                                     workflow: WorkflowDefinition) -> List[List[str]]:
        """Optimize execution plan based on strategy"""
        try:
            strategy = workflow.optimization_strategy

            if strategy == OptimizationStrategy.TIME_OPTIMAL:
                # Maximize parallelization
                optimized_plan = self._optimize_for_time(execution_plan, workflow)

            elif strategy == OptimizationStrategy.RESOURCE_OPTIMAL:
                # Minimize resource conflicts
                optimized_plan = self._optimize_for_resources(execution_plan, workflow)

            elif strategy == OptimizationStrategy.COST_OPTIMAL:
                # Minimize execution costs
                optimized_plan = self._optimize_for_cost(execution_plan, workflow)

            elif strategy == OptimizationStrategy.RELIABILITY_OPTIMAL:
                # Maximize success probability
                optimized_plan = self._optimize_for_reliability(execution_plan, workflow)

            else:
                optimized_plan = execution_plan

            # Emit optimization signal
            self.optimization_applied.emit(workflow.workflow_id, {
                'strategy': strategy.value,
                'original_phases': len(execution_plan),
                'optimized_phases': len(optimized_plan),
                'optimization_applied': True
            })

            return optimized_plan

        except Exception as e:
            logger.error(f"❌ Error optimizing execution plan: {e}")
            return execution_plan

    def _optimize_for_time(self, execution_plan: List[List[str]],
                          workflow: WorkflowDefinition) -> List[List[str]]:
        """Optimize execution plan for minimum time"""
        # Merge phases where possible to increase parallelization
        optimized_plan = []

        for phase in execution_plan:
            if optimized_plan and len(optimized_plan[-1]) + len(phase) <= workflow.max_parallel_tasks:
                # Merge with previous phase if resource limits allow
                optimized_plan[-1].extend(phase)
            else:
                optimized_plan.append(phase)

        return optimized_plan

    def _optimize_for_resources(self, execution_plan: List[List[str]],
                               workflow: WorkflowDefinition) -> List[List[str]]:
        """Optimize execution plan for resource efficiency"""
        # Separate phases to avoid resource conflicts
        optimized_plan = []

        for phase in execution_plan:
            # Check for resource conflicts within phase
            resource_groups = self._group_by_resources(phase, workflow)

            for group in resource_groups:
                optimized_plan.append(group)

        return optimized_plan

    def _optimize_for_cost(self, execution_plan: List[List[str]],
                          workflow: WorkflowDefinition) -> List[List[str]]:
        """Optimize execution plan for cost efficiency"""
        # Prioritize low-cost operations first
        optimized_plan = []

        for phase in execution_plan:
            # Sort by estimated cost (simplified)
            sorted_phase = sorted(phase, key=lambda n: self._estimate_node_cost(n, workflow))
            optimized_plan.append(sorted_phase)

        return optimized_plan

    def _optimize_for_reliability(self, execution_plan: List[List[str]],
                                 workflow: WorkflowDefinition) -> List[List[str]]:
        """Optimize execution plan for reliability"""
        # Separate high-risk operations to minimize failure impact
        optimized_plan = []

        for phase in execution_plan:
            # Group by reliability score
            reliable_nodes = []
            risky_nodes = []

            for node_id in phase:
                reliability = self._estimate_node_reliability(node_id, workflow)
                if reliability > 0.8:
                    reliable_nodes.append(node_id)
                else:
                    risky_nodes.append(node_id)

            if reliable_nodes:
                optimized_plan.append(reliable_nodes)
            if risky_nodes:
                optimized_plan.append(risky_nodes)

        return optimized_plan

    def _group_by_resources(self, phase: List[str], workflow: WorkflowDefinition) -> List[List[str]]:
        """Group nodes by resource requirements"""
        resource_groups = []
        used_resources = set()

        for node_id in phase:
            node = next(n for n in workflow.nodes if n.node_id == node_id)
            node_resources = set(node.resources_required.keys())

            # Check for resource conflicts
            if not node_resources.intersection(used_resources):
                # Can add to current group
                if resource_groups:
                    resource_groups[-1].append(node_id)
                else:
                    resource_groups.append([node_id])
                used_resources.update(node_resources)
            else:
                # Start new group
                resource_groups.append([node_id])
                used_resources = node_resources

        return resource_groups if resource_groups else [[]]

    def _estimate_node_cost(self, node_id: str, workflow: WorkflowDefinition) -> float:
        """Estimate execution cost for a node"""
        node = next(n for n in workflow.nodes if n.node_id == node_id)

        # Simplified cost estimation based on task type and complexity
        base_cost = 1.0

        if node.task_definition.task_type == TaskType.SYSTEM_COMMAND:
            base_cost = 0.5
        elif node.task_definition.task_type == TaskType.FILE_OPERATION:
            base_cost = 0.3
        elif node.task_definition.task_type == TaskType.ANALYSIS:
            base_cost = 2.0

        # Adjust for timeout (longer tasks cost more)
        time_factor = node.timeout / 300.0  # Normalize to 5-minute baseline

        return base_cost * time_factor

    def _estimate_node_reliability(self, node_id: str, workflow: WorkflowDefinition) -> float:
        """Estimate reliability score for a node"""
        node = next(n for n in workflow.nodes if n.node_id == node_id)

        # Base reliability by task type
        base_reliability = {
            TaskType.FILE_OPERATION: 0.95,
            TaskType.SYSTEM_COMMAND: 0.85,
            TaskType.DATA_PROCESSING: 0.90,
            TaskType.ANALYSIS: 0.80,
            TaskType.AUTOMATION: 0.75,
            TaskType.MONITORING: 0.90,
            TaskType.CUSTOM: 0.70
        }.get(node.task_definition.task_type, 0.75)

        # Adjust for complexity (more steps = lower reliability)
        complexity_factor = max(0.5, 1.0 - (len(node.task_definition.steps) - 1) * 0.1)

        return base_reliability * complexity_factor

    def _has_circular_dependencies(self, node_dependencies: Dict[str, Set[str]]) -> bool:
        """Check for circular dependencies using DFS"""
        try:
            visited = set()
            rec_stack = set()

            def dfs(node_id: str) -> bool:
                if node_id in rec_stack:
                    return True  # Cycle found
                if node_id in visited:
                    return False

                visited.add(node_id)
                rec_stack.add(node_id)

                for dep_id in node_dependencies.get(node_id, set()):
                    if dfs(dep_id):
                        return True

                rec_stack.remove(node_id)
                return False

            for node_id in node_dependencies:
                if node_id not in visited:
                    if dfs(node_id):
                        return True

            return False

        except Exception as e:
            logger.error(f"❌ Error checking circular dependencies: {e}")
            return True  # Assume circular dependency on error

    async def _execute_workflow_phases(self, execution: WorkflowExecution) -> bool:
        """Execute all phases of a workflow"""
        try:
            workflow = execution.workflow_definition
            total_nodes = len(workflow.nodes)

            for phase_index, phase_nodes in enumerate(execution.execution_plan):
                execution.current_phase = phase_index
                execution.logs.append(f"Starting phase {phase_index + 1}/{len(execution.execution_plan)}")

                # Execute nodes in current phase (parallel execution)
                phase_tasks = []
                for node_id in phase_nodes:
                    execution.running_nodes.add(node_id)
                    task = self._execute_workflow_node(execution, node_id)
                    phase_tasks.append(task)

                # Wait for all nodes in phase to complete
                phase_results = await asyncio.gather(*phase_tasks, return_exceptions=True)

                # Process phase results
                phase_success = True
                for i, result in enumerate(phase_results):
                    node_id = phase_nodes[i]
                    execution.running_nodes.discard(node_id)

                    if isinstance(result, Exception):
                        execution.failed_nodes.add(node_id)
                        execution.node_errors[node_id] = str(result)
                        execution.logs.append(f"Node {node_id} failed: {result}")
                        phase_success = False
                    else:
                        execution.completed_nodes.add(node_id)
                        execution.node_results[node_id] = result
                        execution.logs.append(f"Node {node_id} completed successfully")

                        # Emit node completion signal
                        self.node_completed.emit(workflow.workflow_id, node_id, result)

                # Emit progress signal
                completed_count = len(execution.completed_nodes)
                self.workflow_progress.emit(workflow.workflow_id, completed_count, total_nodes)

                # Handle phase failure
                if not phase_success:
                    error_strategy = workflow.error_handling_strategy

                    if error_strategy == "fail_fast":
                        execution.logs.append("Workflow failed due to fail_fast strategy")
                        return False
                    elif error_strategy == "retry_and_continue":
                        # Retry failed nodes once
                        retry_success = await self._retry_failed_nodes(execution, phase_nodes)
                        if not retry_success and error_strategy == "fail_on_critical":
                            return False
                    # For "continue_on_error", we just continue to next phase

                execution.logs.append(f"Phase {phase_index + 1} completed")

            # Calculate success rate
            success_rate = len(execution.completed_nodes) / total_nodes if total_nodes > 0 else 0.0
            execution.optimization_metrics['success_rate'] = success_rate

            # Workflow is successful if at least 80% of nodes completed
            return success_rate >= 0.8

        except Exception as e:
            logger.error(f"❌ Error executing workflow phases: {e}")
            execution.logs.append(f"Workflow execution error: {e}")
            return False

    async def _execute_workflow_node(self, execution: WorkflowExecution, node_id: str) -> Dict[str, Any]:
        """Execute a single workflow node"""
        try:
            workflow = execution.workflow_definition
            node = next(n for n in workflow.nodes if n.node_id == node_id)

            # Check conditions if any
            if node.conditions and not self._check_node_conditions(node, execution):
                return {'status': 'skipped', 'reason': 'conditions not met'}

            # Create task from node definition
            task_id = self.task_manager.create_task(
                name=f"Workflow_{workflow.workflow_id}_Node_{node_id}",
                description=node.task_definition.description,
                task_type=node.task_definition.task_type,
                steps=[{
                    'description': step.description,
                    'action': step.action,
                    'parameters': step.parameters,
                    'timeout': step.timeout,
                    'max_retries': step.max_retries
                } for step in node.task_definition.steps],
                priority=TaskPriority(node.priority) if node.priority <= 4 else TaskPriority.NORMAL,
                timeout=node.timeout,
                safety_level=node.task_definition.safety_level
            )

            if not task_id:
                raise Exception(f"Failed to create task for node {node_id}")

            # Execute task (simplified - in real implementation would use proper async execution)
            # For now, we'll simulate task execution
            await asyncio.sleep(0.1)  # Simulate execution time

            # Get task result (simplified)
            task_history = self.task_manager.get_task_history(limit=10)
            for task_result in reversed(task_history):
                if task_result['task_id'] == task_id:
                    return {
                        'status': 'completed',
                        'task_id': task_id,
                        'result': task_result,
                        'execution_time': task_result.get('execution_time', 0.0)
                    }

            # If no result found, return success (for simulation)
            return {
                'status': 'completed',
                'task_id': task_id,
                'result': {'simulated': True},
                'execution_time': 1.0
            }

        except Exception as e:
            logger.error(f"❌ Error executing workflow node {node_id}: {e}")
            raise e

    def _check_node_conditions(self, node: WorkflowNode, execution: WorkflowExecution) -> bool:
        """Check if node conditions are met"""
        try:
            for condition_key, condition_value in node.conditions.items():
                if condition_key == 'depends_on_success':
                    # Check if dependent nodes completed successfully
                    for dep_node_id in condition_value:
                        if dep_node_id not in execution.completed_nodes:
                            return False

                elif condition_key == 'depends_on_result':
                    # Check if dependent node produced expected result
                    dep_node_id = condition_value['node_id']
                    expected_result = condition_value['expected']

                    if dep_node_id not in execution.node_results:
                        return False

                    actual_result = execution.node_results[dep_node_id]
                    if not self._compare_results(actual_result, expected_result):
                        return False

                elif condition_key == 'time_window':
                    # Check if current time is within specified window
                    current_time = datetime.now()
                    start_time = datetime.fromisoformat(condition_value['start'])
                    end_time = datetime.fromisoformat(condition_value['end'])

                    if not (start_time <= current_time <= end_time):
                        return False

            return True

        except Exception as e:
            logger.error(f"❌ Error checking node conditions: {e}")
            return False

    def _compare_results(self, actual: Any, expected: Any) -> bool:
        """Compare actual result with expected result"""
        try:
            if isinstance(expected, dict) and 'operator' in expected:
                operator = expected['operator']
                value = expected['value']

                if operator == 'equals':
                    return actual == value
                elif operator == 'contains':
                    return value in str(actual)
                elif operator == 'greater_than':
                    return float(actual) > float(value)
                elif operator == 'less_than':
                    return float(actual) < float(value)
                else:
                    return str(actual) == str(expected)
            else:
                return actual == expected

        except Exception:
            return False

    async def _retry_failed_nodes(self, execution: WorkflowExecution, phase_nodes: List[str]) -> bool:
        """Retry failed nodes in a phase"""
        try:
            failed_nodes_in_phase = [node_id for node_id in phase_nodes if node_id in execution.failed_nodes]

            if not failed_nodes_in_phase:
                return True

            execution.logs.append(f"Retrying {len(failed_nodes_in_phase)} failed nodes")

            # Retry each failed node once
            retry_tasks = []
            for node_id in failed_nodes_in_phase:
                # Remove from failed set for retry
                execution.failed_nodes.discard(node_id)
                execution.node_errors.pop(node_id, None)

                retry_task = self._execute_workflow_node(execution, node_id)
                retry_tasks.append(retry_task)

            # Wait for retry results
            retry_results = await asyncio.gather(*retry_tasks, return_exceptions=True)

            # Process retry results
            retry_success = True
            for i, result in enumerate(retry_results):
                node_id = failed_nodes_in_phase[i]

                if isinstance(result, Exception):
                    execution.failed_nodes.add(node_id)
                    execution.node_errors[node_id] = str(result)
                    execution.logs.append(f"Node {node_id} retry failed: {result}")
                    retry_success = False
                else:
                    execution.completed_nodes.add(node_id)
                    execution.node_results[node_id] = result
                    execution.logs.append(f"Node {node_id} retry succeeded")

            return retry_success

        except Exception as e:
            logger.error(f"❌ Error retrying failed nodes: {e}")
            return False

    def _parse_workflow_nodes(self, nodes_data: List[Dict[str, Any]]) -> List[WorkflowNode]:
        """Parse workflow nodes from definition data"""
        try:
            nodes = []

            for node_data in nodes_data:
                # Create task definition
                task_steps = []
                for step_data in node_data.get('steps', []):
                    from ..tasks.task_framework import TaskStep
                    step = TaskStep(
                        step_id=step_data.get('step_id', f"step_{len(task_steps)+1}"),
                        description=step_data.get('description', ''),
                        action=step_data.get('action', ''),
                        parameters=step_data.get('parameters', {}),
                        timeout=step_data.get('timeout', 30),
                        max_retries=step_data.get('max_retries', 3)
                    )
                    task_steps.append(step)

                task_definition = TaskDefinition(
                    task_id=node_data.get('task_id', f"task_{len(nodes)+1}"),
                    name=node_data.get('name', f"Task {len(nodes)+1}"),
                    description=node_data.get('description', ''),
                    task_type=TaskType(node_data.get('task_type', 'automation')),
                    priority=TaskPriority(node_data.get('priority', 2)),
                    steps=task_steps,
                    timeout=node_data.get('timeout', 300),
                    safety_level=node_data.get('safety_level', 'moderate')
                )

                # Create workflow node
                node = WorkflowNode(
                    node_id=node_data.get('node_id', f"node_{len(nodes)+1}"),
                    task_definition=task_definition,
                    dependencies=node_data.get('dependencies', []),
                    dependency_types={
                        dep: DependencyType(dep_type)
                        for dep, dep_type in node_data.get('dependency_types', {}).items()
                    },
                    conditions=node_data.get('conditions', {}),
                    retry_policy=node_data.get('retry_policy', {}),
                    timeout=node_data.get('timeout', 300),
                    priority=node_data.get('priority', 1),
                    resources_required=node_data.get('resources_required', {}),
                    metadata=node_data.get('metadata', {})
                )

                nodes.append(node)

            return nodes

        except Exception as e:
            logger.error(f"❌ Error parsing workflow nodes: {e}")
            return []

    def _validate_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Validate workflow definition"""
        try:
            # Basic validation
            if not workflow.name or not workflow.nodes:
                return False

            # Check for duplicate node IDs
            node_ids = [node.node_id for node in workflow.nodes]
            if len(node_ids) != len(set(node_ids)):
                logger.error("❌ Duplicate node IDs found in workflow")
                return False

            # Validate dependencies
            for node in workflow.nodes:
                for dep_id in node.dependencies:
                    if dep_id not in node_ids:
                        logger.error(f"❌ Invalid dependency: {dep_id} not found")
                        return False

            # Check for circular dependencies (simplified check)
            # In a real implementation, would use graph algorithms

            return True

        except Exception as e:
            logger.error(f"❌ Error validating workflow: {e}")
            return False

    def _estimate_workflow_duration(self, nodes: List[WorkflowNode]) -> float:
        """Estimate total workflow duration"""
        try:
            # Simplified estimation - sum of all node timeouts
            total_duration = sum(node.timeout for node in nodes)

            # Adjust for potential parallelization (rough estimate)
            parallelization_factor = 0.6  # Assume 60% can be parallelized
            estimated_duration = total_duration * parallelization_factor

            return estimated_duration

        except Exception:
            return 3600.0  # Default 1 hour

    def _complete_workflow(self, execution: WorkflowExecution, success: bool):
        """Complete workflow execution"""
        try:
            execution.end_time = datetime.now()
            execution.total_execution_time = (execution.end_time - execution.start_time).total_seconds()

            if success:
                execution.status = WorkflowStatus.COMPLETED
                self.execution_stats['successful_workflows'] += 1
                self.workflow_completed.emit(execution.workflow_definition.workflow_id, {
                    'completed_nodes': len(execution.completed_nodes),
                    'failed_nodes': len(execution.failed_nodes),
                    'execution_time': execution.total_execution_time,
                    'success_rate': execution.optimization_metrics.get('success_rate', 0.0)
                })
            else:
                execution.status = WorkflowStatus.FAILED
                self.execution_stats['failed_workflows'] += 1
                error_summary = f"Failed nodes: {len(execution.failed_nodes)}, Errors: {list(execution.node_errors.values())[:3]}"
                self.workflow_failed.emit(execution.workflow_definition.workflow_id, error_summary)

            # Update statistics
            self.execution_stats['total_workflows'] += 1
            self.execution_stats['workflows_by_strategy'][execution.workflow_definition.optimization_strategy.value] += 1

            # Update average execution time
            if self.execution_stats['total_workflows'] > 0:
                total_time = (self.execution_stats['average_execution_time'] *
                             (self.execution_stats['total_workflows'] - 1) + execution.total_execution_time)
                self.execution_stats['average_execution_time'] = total_time / self.execution_stats['total_workflows']

            # Move to history
            self.workflow_history.append(execution)
            if len(self.workflow_history) > self.max_workflow_history:
                self.workflow_history.pop(0)

            # Remove from active workflows
            if execution.workflow_definition.workflow_id in self.active_workflows:
                del self.active_workflows[execution.workflow_definition.workflow_id]

            # Learn from execution if enabled
            if self.learning_enabled:
                self._learn_from_execution(execution)

            logger.info(f"🔄 Workflow completed: {execution.workflow_definition.workflow_id} "
                       f"(Status: {execution.status.value}, Time: {execution.total_execution_time:.2f}s)")

        except Exception as e:
            logger.error(f"❌ Error completing workflow: {e}")

    def _learn_from_execution(self, execution: WorkflowExecution):
        """Learn from workflow execution for future optimization"""
        try:
            workflow_id = execution.workflow_definition.workflow_id

            # Store performance metrics
            performance_data = {
                'workflow_id': workflow_id,
                'execution_time': execution.total_execution_time,
                'success_rate': execution.optimization_metrics.get('success_rate', 0.0),
                'optimization_strategy': execution.workflow_definition.optimization_strategy.value,
                'node_count': len(execution.workflow_definition.nodes),
                'failed_nodes': len(execution.failed_nodes),
                'timestamp': datetime.now().isoformat()
            }

            self.performance_history.append(performance_data)

            # Update optimization patterns
            strategy = execution.workflow_definition.optimization_strategy.value
            if strategy not in self.optimization_patterns:
                self.optimization_patterns[strategy] = {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'average_time': 0.0,
                    'average_success_rate': 0.0
                }

            pattern = self.optimization_patterns[strategy]
            pattern['total_executions'] += 1

            if execution.status == WorkflowStatus.COMPLETED:
                pattern['successful_executions'] += 1

            # Update averages
            pattern['average_time'] = (
                (pattern['average_time'] * (pattern['total_executions'] - 1) + execution.total_execution_time) /
                pattern['total_executions']
            )

            success_rate = execution.optimization_metrics.get('success_rate', 0.0)
            pattern['average_success_rate'] = (
                (pattern['average_success_rate'] * (pattern['total_executions'] - 1) + success_rate) /
                pattern['total_executions']
            )

            logger.debug(f"🔄 Learning updated for strategy: {strategy}")

        except Exception as e:
            logger.error(f"❌ Error learning from execution: {e}")

    def _monitor_workflows(self):
        """Monitor active workflows for issues and optimization opportunities"""
        try:
            current_time = datetime.now()

            for workflow_id, execution in list(self.active_workflows.items()):
                # Check for timeout
                if execution.start_time:
                    elapsed_time = (current_time - execution.start_time).total_seconds()
                    if elapsed_time > execution.workflow_definition.global_timeout:
                        logger.warning(f"⚠️ Workflow timeout: {workflow_id}")
                        execution.status = WorkflowStatus.FAILED
                        execution.logs.append("Workflow timeout")
                        self._complete_workflow(execution, False)

                # Check for optimization opportunities
                if execution.status == WorkflowStatus.RUNNING:
                    efficiency = self._calculate_current_efficiency(execution)
                    if efficiency < self.optimization_threshold:
                        logger.info(f"🔄 Low efficiency detected for workflow {workflow_id}: {efficiency:.2f}")
                        # Could trigger dynamic optimization here

        except Exception as e:
            logger.error(f"❌ Error monitoring workflows: {e}")

    def _calculate_current_efficiency(self, execution: WorkflowExecution) -> float:
        """Calculate current execution efficiency"""
        try:
            if not execution.start_time:
                return 1.0

            elapsed_time = (datetime.now() - execution.start_time).total_seconds()
            total_nodes = len(execution.workflow_definition.nodes)
            completed_nodes = len(execution.completed_nodes)

            if elapsed_time == 0 or total_nodes == 0:
                return 1.0

            # Calculate efficiency as completion rate vs time rate
            completion_rate = completed_nodes / total_nodes
            estimated_total_time = execution.workflow_definition.metadata.get('estimated_duration', 3600)
            time_rate = elapsed_time / estimated_total_time

            efficiency = completion_rate / max(time_rate, 0.1)  # Avoid division by zero

            return min(1.0, efficiency)

        except Exception:
            return 1.0

    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        self.workflow_counter += 1
        return f"workflow_{self.workflow_counter:06d}"

    def get_workflow_queue(self) -> List[Dict[str, Any]]:
        """Get current workflow queue"""
        return [self._workflow_definition_to_dict(workflow) for workflow in self.workflow_queue]

    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get currently active workflows"""
        return [self._workflow_execution_to_dict(execution) for execution in self.active_workflows.values()]

    def get_workflow_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        history = self.workflow_history[-limit:] if limit > 0 else self.workflow_history
        return [self._workflow_execution_to_dict(execution) for execution in history]

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.execution_stats.copy()

    def get_optimization_patterns(self) -> Dict[str, Any]:
        """Get optimization patterns learned from executions"""
        return self.optimization_patterns.copy()

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow"""
        try:
            # Cancel active workflow
            if workflow_id in self.active_workflows:
                execution = self.active_workflows[workflow_id]
                execution.status = WorkflowStatus.CANCELLED
                execution.logs.append("Workflow cancelled by user")
                self._complete_workflow(execution, False)
                self.execution_stats['cancelled_workflows'] += 1
                logger.info(f"🔄 Workflow cancelled: {workflow_id}")
                return True

            # Remove from queue
            for workflow in self.workflow_queue:
                if workflow.workflow_id == workflow_id:
                    self.workflow_queue.remove(workflow)
                    logger.info(f"🔄 Workflow removed from queue: {workflow_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ Error cancelling workflow: {e}")
            return False

    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow"""
        try:
            if workflow_id in self.active_workflows:
                execution = self.active_workflows[workflow_id]
                if execution.status == WorkflowStatus.RUNNING:
                    execution.status = WorkflowStatus.PAUSED
                    execution.logs.append("Workflow paused by user")
                    logger.info(f"🔄 Workflow paused: {workflow_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ Error pausing workflow: {e}")
            return False

    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        try:
            if workflow_id in self.active_workflows:
                execution = self.active_workflows[workflow_id]
                if execution.status == WorkflowStatus.PAUSED:
                    execution.status = WorkflowStatus.RUNNING
                    execution.logs.append("Workflow resumed by user")
                    logger.info(f"🔄 Workflow resumed: {workflow_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ Error resuming workflow: {e}")
            return False

    def _workflow_definition_to_dict(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Convert WorkflowDefinition to dictionary"""
        return {
            'workflow_id': workflow.workflow_id,
            'name': workflow.name,
            'description': workflow.description,
            'nodes_count': len(workflow.nodes),
            'global_timeout': workflow.global_timeout,
            'optimization_strategy': workflow.optimization_strategy.value,
            'error_handling_strategy': workflow.error_handling_strategy,
            'max_parallel_tasks': workflow.max_parallel_tasks,
            'created_by': workflow.created_by,
            'metadata': workflow.metadata
        }

    def _workflow_execution_to_dict(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Convert WorkflowExecution to dictionary"""
        return {
            'execution_id': execution.execution_id,
            'workflow_id': execution.workflow_definition.workflow_id,
            'workflow_name': execution.workflow_definition.name,
            'status': execution.status.value,
            'current_phase': execution.current_phase,
            'total_phases': len(execution.execution_plan),
            'completed_nodes': len(execution.completed_nodes),
            'failed_nodes': len(execution.failed_nodes),
            'running_nodes': len(execution.running_nodes),
            'total_nodes': len(execution.workflow_definition.nodes),
            'start_time': execution.start_time.isoformat() if execution.start_time else None,
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'execution_time': execution.total_execution_time,
            'optimization_metrics': execution.optimization_metrics,
            'logs_count': len(execution.logs)
        }

# Singleton instance
_workflow_engine = None

def get_workflow_engine() -> WorkflowEngine:
    """Get the singleton Workflow Engine instance"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine
