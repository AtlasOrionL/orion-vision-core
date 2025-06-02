"""
Unit Tests for Task Core Modules

This module tests task core functionality including definitions, execution, and orchestration.
Part of Sprint 9.1.1.1 comprehensive testing suite.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch

from src.jobone.vision_core.tasks.core import (
    TaskDefinition, TaskExecution, TaskStatus, TaskPriority, WorkflowStatus
)
from src.jobone.vision_core.tasks.orchestration import TaskScheduler, TaskExecutor
from src.jobone.vision_core.tasks.workflow import WorkflowEngine, WorkflowBuilder


class TestTaskDefinition:
    """Test task definition"""
    
    def test_valid_task_creation(self, sample_task_definition, test_assertions):
        """Test creating valid task definition"""
        test_assertions.assert_task_definition_valid(sample_task_definition)
    
    def test_task_validation(self):
        """Test task validation"""
        # Valid task
        task = TaskDefinition(task_name="Test", task_type="test")
        assert task.validate()
        
        # Invalid tasks
        with pytest.raises(ValueError):
            TaskDefinition(task_name="", task_type="test")  # Empty name
        
        with pytest.raises(ValueError):
            TaskDefinition(task_name="Test", task_type="")  # Empty type
        
        with pytest.raises(ValueError):
            TaskDefinition(task_name="Test", task_type="test", timeout=-1)  # Negative timeout
    
    def test_task_serialization(self, sample_task_definition):
        """Test task serialization"""
        task_dict = sample_task_definition.to_dict()
        
        assert task_dict['task_name'] == sample_task_definition.task_name
        assert task_dict['task_type'] == sample_task_definition.task_type
        assert task_dict['priority'] == sample_task_definition.priority.value
        
        # Test deserialization
        restored_task = TaskDefinition.from_dict(task_dict)
        assert restored_task.task_name == sample_task_definition.task_name
        assert restored_task.priority == sample_task_definition.priority
    
    def test_task_dependencies(self):
        """Test task dependency management"""
        task = TaskDefinition(task_name="Test", task_type="test")
        
        # Add dependencies
        task.add_dependency("dep_001")
        task.add_dependency("dep_002")
        assert len(task.dependencies) == 2
        assert "dep_001" in task.dependencies
        
        # Remove dependency
        task.remove_dependency("dep_001")
        assert len(task.dependencies) == 1
        assert "dep_001" not in task.dependencies
    
    def test_task_metadata(self):
        """Test task metadata management"""
        task = TaskDefinition(task_name="Test", task_type="test")
        
        # Set metadata
        task.set_metadata("key1", "value1")
        task.set_metadata("key2", {"nested": "value"})
        
        # Get metadata
        assert task.get_metadata("key1") == "value1"
        assert task.get_metadata("key2")["nested"] == "value"
        assert task.get_metadata("nonexistent", "default") == "default"
    
    def test_task_expiration(self):
        """Test task expiration"""
        # Task with deadline in the past
        past_deadline = time.time() - 3600  # 1 hour ago
        task = TaskDefinition(
            task_name="Expired Task",
            task_type="test",
            deadline=past_deadline
        )
        assert task.is_expired()
        
        # Task with future deadline
        future_deadline = time.time() + 3600  # 1 hour from now
        task = TaskDefinition(
            task_name="Future Task",
            task_type="test",
            deadline=future_deadline
        )
        assert not task.is_expired()


class TestTaskExecution:
    """Test task execution"""
    
    def test_execution_creation(self):
        """Test task execution creation"""
        execution = TaskExecution(task_id="test_task_001")
        assert execution.task_id == "test_task_001"
        assert execution.status == TaskStatus.PENDING
        assert execution.progress_percentage == 0.0
    
    def test_execution_lifecycle(self):
        """Test complete execution lifecycle"""
        execution = TaskExecution(task_id="test_task_001")
        
        # Start execution
        execution.start_execution("test_agent", "test_service")
        assert execution.status == TaskStatus.RUNNING
        assert execution.assigned_agent == "test_agent"
        assert execution.start_time is not None
        assert execution.is_running()
        
        # Update progress
        execution.update_progress(50.0, "Halfway done")
        assert execution.progress_percentage == 50.0
        assert execution.progress_message == "Halfway done"
        
        # Complete execution
        output_data = {"result": "success", "value": 42}
        execution.complete_execution(output_data)
        assert execution.status == TaskStatus.COMPLETED
        assert execution.is_completed()
        assert execution.is_finished()
        assert execution.output_data == output_data
        assert execution.duration is not None
    
    def test_execution_failure(self):
        """Test execution failure"""
        execution = TaskExecution(task_id="test_task_001")
        execution.start_execution("test_agent")
        
        # Fail execution
        error_details = {"error_code": "TEST_ERROR", "details": "Test failure"}
        execution.fail_execution("Test error message", error_details)
        
        assert execution.status == TaskStatus.FAILED
        assert execution.is_failed()
        assert execution.is_finished()
        assert execution.error_message == "Test error message"
        assert execution.error_details == error_details
    
    def test_execution_timeout(self):
        """Test execution timeout"""
        execution = TaskExecution(task_id="test_task_001")
        execution.start_execution("test_agent")
        
        execution.timeout_execution()
        assert execution.status == TaskStatus.TIMEOUT
        assert execution.is_failed()
        assert execution.error_message == "Task execution timed out"
    
    def test_execution_cancellation(self):
        """Test execution cancellation"""
        execution = TaskExecution(task_id="test_task_001")
        execution.start_execution("test_agent")
        
        execution.cancel_execution()
        assert execution.status == TaskStatus.CANCELLED
        assert execution.is_finished()
    
    def test_execution_retry(self):
        """Test execution retry mechanism"""
        execution = TaskExecution(task_id="test_task_001")
        execution.start_execution("test_agent")
        
        # First failure
        execution.fail_execution("First failure")
        initial_attempt = execution.attempt_number
        
        # Add retry
        execution.add_retry_attempt("First failure")
        assert execution.attempt_number == initial_attempt + 1
        assert execution.status == TaskStatus.PENDING
        assert len(execution.retry_history) == 1
        
        # Retry execution
        execution.start_execution("test_agent")
        execution.complete_execution({"result": "success"})
        assert execution.is_completed()
    
    def test_execution_performance_metrics(self):
        """Test performance metrics tracking"""
        execution = TaskExecution(task_id="test_task_001")
        execution.start_execution("test_agent")
        
        # Update performance metrics
        execution.update_performance_metrics(
            cpu_usage=25.5,
            memory_usage=128.0,
            network_usage=1024.0
        )
        
        assert execution.cpu_usage == 25.5
        assert execution.memory_usage == 128.0
        assert execution.network_usage == 1024.0
    
    def test_execution_checkpoints(self):
        """Test execution checkpoints"""
        execution = TaskExecution(task_id="test_task_001")
        execution.start_execution("test_agent")
        
        initial_checkpoints = len(execution.checkpoints)
        
        # Update progress (creates checkpoint)
        execution.update_progress(25.0, "Quarter done")
        execution.update_progress(50.0, "Half done")
        
        assert len(execution.checkpoints) > initial_checkpoints
        
        # Check checkpoint data
        latest_checkpoint = execution.checkpoints[-1]
        assert latest_checkpoint['percentage'] == 50.0
        assert latest_checkpoint['message'] == "Half done"
    
    def test_execution_summary(self):
        """Test execution summary"""
        execution = TaskExecution(task_id="test_task_001")
        execution.start_execution("test_agent")
        execution.update_progress(75.0)
        execution.complete_execution()
        
        summary = execution.get_execution_summary()
        assert summary['task_id'] == "test_task_001"
        assert summary['status'] == TaskStatus.COMPLETED.value
        assert summary['assigned_agent'] == "test_agent"
        assert summary['progress_percentage'] == 100.0  # Completed sets to 100%


@pytest.mark.asyncio
class TestTaskScheduler:
    """Test task scheduler"""
    
    async def test_scheduler_lifecycle(self, test_logger):
        """Test scheduler start/stop lifecycle"""
        scheduler = TaskScheduler(test_logger)
        
        # Start scheduler
        await scheduler.start()
        assert scheduler.running
        
        # Stop scheduler
        await scheduler.stop()
        assert not scheduler.running
    
    async def test_task_submission(self, task_scheduler, sample_task_definition):
        """Test task submission to scheduler"""
        result = task_scheduler.submit_task(sample_task_definition)
        assert result is True
        
        stats = task_scheduler.get_scheduler_stats()
        assert stats['pending_tasks'] == 1
        assert stats['stats']['total_tasks_scheduled'] == 1
    
    async def test_task_scheduling_priority(self, task_scheduler, test_data_generator):
        """Test priority-based task scheduling"""
        tasks = test_data_generator.generate_task_definitions(5)
        
        # Submit tasks with different priorities
        for task in tasks:
            task_scheduler.submit_task(task)
        
        # Get next task (should be highest priority)
        next_task = task_scheduler.get_next_task()
        assert next_task is not None
        
        # Should be one of the high priority tasks
        assert next_task.priority.value >= TaskPriority.NORMAL.value
    
    async def test_task_dependencies(self, task_scheduler):
        """Test task dependency handling"""
        # Create dependent tasks
        task1 = TaskDefinition(task_name="Task 1", task_type="test")
        task2 = TaskDefinition(task_name="Task 2", task_type="test")
        task2.add_dependency(task1.task_id)
        
        # Submit both tasks
        task_scheduler.submit_task(task1)
        task_scheduler.submit_task(task2)
        
        # Task 1 should be available first
        next_task = task_scheduler.get_next_task()
        assert next_task.task_id == task1.task_id
        
        # Task 2 should not be available until task 1 completes
        next_task = task_scheduler.get_next_task()
        assert next_task is None  # Task 2 blocked by dependency
        
        # Complete task 1
        execution = task_scheduler.start_task_execution(task1, "test_agent")
        task_scheduler.complete_task_execution(task1.task_id, {"result": "done"})
        
        # Now task 2 should be available
        next_task = task_scheduler.get_next_task()
        assert next_task is not None
        assert next_task.task_id == task2.task_id
    
    async def test_task_cancellation(self, task_scheduler, sample_task_definition):
        """Test task cancellation"""
        # Submit task
        task_scheduler.submit_task(sample_task_definition)
        
        # Cancel task
        result = task_scheduler.cancel_task(sample_task_definition.task_id)
        assert result is True
        
        # Task should no longer be available
        next_task = task_scheduler.get_next_task()
        assert next_task is None


@pytest.mark.asyncio
class TestTaskExecutor:
    """Test task executor"""
    
    async def test_executor_lifecycle(self, test_logger):
        """Test executor start/stop lifecycle"""
        executor = TaskExecutor(test_logger)
        
        await executor.start()
        assert executor.running
        
        await executor.stop()
        assert not executor.running
    
    async def test_agent_registration(self, task_executor):
        """Test agent registration"""
        capabilities = ["python", "data_processing"]
        task_executor.register_agent("test_agent_001", capabilities, 3)
        
        stats = task_executor.get_executor_stats()
        assert stats['available_agents'] == 1
        
        # Test agent unregistration
        task_executor.unregister_agent("test_agent_001")
        stats = task_executor.get_executor_stats()
        assert stats['available_agents'] == 0
    
    async def test_task_execution(self, task_executor, sample_task_definition):
        """Test task execution"""
        # Register agent
        task_executor.register_agent("test_agent_001", ["python", "testing"], 2)
        
        # Execute task
        execution = task_executor.execute_task(sample_task_definition)
        assert execution is not None
        assert execution.assigned_agent == "test_agent_001"
        assert execution.is_running()
        
        # Complete execution
        result = task_executor.complete_task_execution(
            sample_task_definition.task_id,
            {"result": "completed"}
        )
        assert result is True
    
    async def test_load_balancing(self, task_executor, test_data_generator):
        """Test load balancing across agents"""
        # Register multiple agents
        task_executor.register_agent("agent_001", ["python"], 2)
        task_executor.register_agent("agent_002", ["python"], 2)
        task_executor.register_agent("agent_003", ["python"], 2)
        
        # Execute multiple tasks
        tasks = test_data_generator.generate_task_definitions(6)
        executions = []
        
        for task in tasks:
            task.required_capabilities = ["python"]
            execution = task_executor.execute_task(task)
            if execution:
                executions.append(execution)
        
        # Check that tasks are distributed across agents
        assigned_agents = {exec.assigned_agent for exec in executions}
        assert len(assigned_agents) > 1  # Tasks distributed across multiple agents


@pytest.mark.asyncio
class TestWorkflowEngine:
    """Test workflow engine"""
    
    async def test_workflow_engine_lifecycle(self, test_logger):
        """Test workflow engine start/stop"""
        engine = WorkflowEngine(test_logger)
        
        await engine.start()
        assert engine.running
        
        await engine.stop()
        assert not engine.running
    
    async def test_workflow_registration(self, workflow_engine, workflow_builder):
        """Test workflow registration"""
        # Build simple workflow
        workflow = (workflow_builder
                   .create_workflow("Test Workflow")
                   .add_task_step("Step 1", "Task 1", "test")
                   .build())
        
        assert workflow is not None
        
        # Register workflow
        result = workflow_engine.register_workflow(workflow)
        assert result is True
        
        stats = workflow_engine.get_engine_stats()
        assert stats['registered_workflows'] == 1


class TestWorkflowBuilder:
    """Test workflow builder"""
    
    def test_workflow_creation(self, workflow_builder):
        """Test workflow creation"""
        workflow_builder.create_workflow("Test Workflow", "A test workflow")
        
        info = workflow_builder.get_current_workflow_info()
        assert info is not None
        assert info['workflow_name'] == "Test Workflow"
        assert info['description'] == "A test workflow"
    
    def test_fluent_api(self, workflow_builder):
        """Test fluent API workflow building"""
        workflow = (workflow_builder
                   .create_workflow("Fluent Test")
                   .add_task_step("Data Processing", "Process Data", "data_processing")
                   .add_task_step("Data Analysis", "Analyze Data", "data_analysis")
                   .set_workflow_config(timeout=1800.0, max_parallel_steps=3)
                   .build())
        
        assert workflow is not None
        assert workflow.workflow_name == "Fluent Test"
        assert len(workflow.steps) == 2
        assert workflow.timeout == 1800.0
        assert workflow.max_parallel_steps == 3
    
    def test_workflow_validation(self, workflow_builder):
        """Test workflow validation"""
        # Valid workflow
        workflow_builder.create_workflow("Valid Workflow")
        workflow_builder.add_task_step("Step 1", "Task 1", "test")
        assert workflow_builder.validate_workflow()
        
        # Invalid workflow (no steps)
        workflow_builder.create_workflow("Invalid Workflow")
        assert not workflow_builder.validate_workflow()
        
        errors = workflow_builder.get_validation_errors()
        assert len(errors) > 0
