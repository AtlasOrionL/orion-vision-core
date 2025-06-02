"""
Performance Benchmarks for Orion Vision Core

This module provides performance testing and benchmarking for all components.
Part of Sprint 9.1.1.1 comprehensive testing suite.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import pytest
import time
import asyncio
import psutil
import threading
from typing import Dict, Any, List
from statistics import mean, median

import sys
sys.path.insert(0, 'src')

from src.jobone.vision_core.agent.core import AgentConfig, AgentLogger
from src.jobone.vision_core.agent.lifecycle import StartupManager, ShutdownManager, HeartbeatManager
from src.jobone.vision_core.tasks.core import TaskDefinition, TaskPriority
from src.jobone.vision_core.tasks.orchestration import TaskScheduler, TaskExecutor
from src.jobone.vision_core.tasks.workflow import WorkflowEngine, WorkflowBuilder
from src.jobone.vision_core.communication.routing import MessageRouter


class PerformanceProfiler:
    """Performance profiling utility"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.start_cpu = None
        self.end_cpu = None
        
    def start_profiling(self):
        """Start performance profiling"""
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = psutil.Process().cpu_percent()
        
    def end_profiling(self):
        """End performance profiling"""
        self.end_time = time.time()
        self.end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.end_cpu = psutil.Process().cpu_percent()
        
    def get_results(self) -> Dict[str, float]:
        """Get profiling results"""
        return {
            'execution_time': self.end_time - self.start_time if self.start_time and self.end_time else 0,
            'memory_usage_mb': self.end_memory - self.start_memory if self.start_memory and self.end_memory else 0,
            'cpu_usage_percent': self.end_cpu if self.end_cpu else 0,
            'peak_memory_mb': self.end_memory if self.end_memory else 0
        }


@pytest.fixture
def profiler():
    """Provide performance profiler"""
    return PerformanceProfiler()


@pytest.mark.performance
class TestAgentPerformance:
    """Test agent performance"""
    
    def test_agent_creation_performance(self, profiler):
        """Test agent creation performance"""
        profiler.start_profiling()
        
        # Create multiple agents
        agents = []
        for i in range(100):
            config = AgentConfig(f"agent_{i:03d}", f"Agent {i}", "TestAgent")
            logger = AgentLogger(f"agent_{i:03d}")
            agents.append((config, logger))
        
        profiler.end_profiling()
        results = profiler.get_results()
        
        # Performance assertions
        assert results['execution_time'] < 1.0, f"Agent creation too slow: {results['execution_time']:.3f}s"
        assert results['memory_usage_mb'] < 50, f"Memory usage too high: {results['memory_usage_mb']:.1f}MB"
        
        print(f"Created 100 agents in {results['execution_time']:.3f}s, using {results['memory_usage_mb']:.1f}MB")
    
    def test_agent_startup_performance(self, profiler):
        """Test agent startup performance"""
        config = AgentConfig("perf_agent", "Performance Agent", "TestAgent")
        logger = AgentLogger("perf_agent")
        startup_mgr = StartupManager(config, logger)
        
        # Test multiple startups
        startup_times = []
        
        for i in range(10):
            profiler.start_profiling()
            result = startup_mgr.execute_startup()
            profiler.end_profiling()
            
            assert result, f"Startup {i} failed"
            results = profiler.get_results()
            startup_times.append(results['execution_time'])
        
        avg_startup_time = mean(startup_times)
        max_startup_time = max(startup_times)
        
        assert avg_startup_time < 0.01, f"Average startup too slow: {avg_startup_time:.3f}s"
        assert max_startup_time < 0.05, f"Max startup too slow: {max_startup_time:.3f}s"
        
        print(f"Average startup time: {avg_startup_time:.3f}s, Max: {max_startup_time:.3f}s")
    
    def test_heartbeat_performance(self, profiler):
        """Test heartbeat performance"""
        config = AgentConfig("heartbeat_agent", "Heartbeat Agent", "TestAgent")
        config.heartbeat_interval = 0.1  # Fast heartbeat
        logger = AgentLogger("heartbeat_agent")
        heartbeat_mgr = HeartbeatManager(config, logger)
        
        profiler.start_profiling()
        
        # Start heartbeat and let it run
        heartbeat_mgr.start_heartbeat()
        time.sleep(1.0)  # Let 10 heartbeats occur
        heartbeat_mgr.stop_heartbeat()
        
        profiler.end_profiling()
        results = profiler.get_results()
        
        stats = heartbeat_mgr.get_heartbeat_stats()
        heartbeat_count = stats['heartbeat_count']
        
        # Performance assertions
        assert heartbeat_count >= 8, f"Too few heartbeats: {heartbeat_count}"
        assert results['memory_usage_mb'] < 10, f"Heartbeat memory usage too high: {results['memory_usage_mb']:.1f}MB"
        
        print(f"Heartbeat performance: {heartbeat_count} beats in 1s, {results['memory_usage_mb']:.1f}MB")


@pytest.mark.performance
@pytest.mark.asyncio
class TestTaskPerformance:
    """Test task performance"""
    
    async def test_task_creation_performance(self, profiler):
        """Test task creation performance"""
        profiler.start_profiling()
        
        # Create many tasks
        tasks = []
        for i in range(1000):
            task = TaskDefinition(
                task_name=f"Task {i}",
                task_type="performance_test",
                priority=TaskPriority(((i % 5) + 1)),
                input_data={"index": i, "data": f"test_data_{i}"}
            )
            tasks.append(task)
        
        profiler.end_profiling()
        results = profiler.get_results()
        
        # Performance assertions
        assert results['execution_time'] < 0.5, f"Task creation too slow: {results['execution_time']:.3f}s"
        assert results['memory_usage_mb'] < 20, f"Memory usage too high: {results['memory_usage_mb']:.1f}MB"
        
        print(f"Created 1000 tasks in {results['execution_time']:.3f}s, using {results['memory_usage_mb']:.1f}MB")
    
    async def test_scheduler_performance(self, profiler):
        """Test scheduler performance"""
        logger = AgentLogger("scheduler_perf")
        scheduler = TaskScheduler(logger)
        
        await scheduler.start()
        
        try:
            # Create tasks
            tasks = []
            for i in range(500):
                task = TaskDefinition(
                    task_name=f"Perf Task {i}",
                    task_type="performance",
                    priority=TaskPriority(((i % 5) + 1))
                )
                tasks.append(task)
            
            profiler.start_profiling()
            
            # Submit all tasks
            for task in tasks:
                scheduler.submit_task(task)
            
            # Get all tasks
            retrieved_tasks = []
            while len(retrieved_tasks) < len(tasks):
                next_task = scheduler.get_next_task()
                if next_task:
                    retrieved_tasks.append(next_task)
                else:
                    break
            
            profiler.end_profiling()
            results = profiler.get_results()
            
            # Performance assertions
            assert len(retrieved_tasks) == len(tasks), f"Task count mismatch: {len(retrieved_tasks)} != {len(tasks)}"
            assert results['execution_time'] < 1.0, f"Scheduling too slow: {results['execution_time']:.3f}s"
            
            print(f"Scheduled 500 tasks in {results['execution_time']:.3f}s")
            
        finally:
            await scheduler.stop()
    
    async def test_executor_performance(self, profiler):
        """Test executor performance"""
        logger = AgentLogger("executor_perf")
        executor = TaskExecutor(logger)
        
        await executor.start()
        
        try:
            # Register multiple agents
            for i in range(10):
                executor.register_agent(f"perf_agent_{i}", ["python"], 5)
            
            # Create tasks
            tasks = []
            for i in range(100):
                task = TaskDefinition(
                    task_name=f"Exec Task {i}",
                    task_type="execution",
                    required_capabilities=["python"]
                )
                tasks.append(task)
            
            profiler.start_profiling()
            
            # Execute all tasks
            executions = []
            for task in tasks:
                execution = executor.execute_task(task)
                if execution:
                    executions.append(execution)
                    # Immediately complete for performance test
                    executor.complete_task_execution(task.task_id, {"result": "done"})
            
            profiler.end_profiling()
            results = profiler.get_results()
            
            # Performance assertions
            assert len(executions) == len(tasks), f"Execution count mismatch: {len(executions)} != {len(tasks)}"
            assert results['execution_time'] < 2.0, f"Execution too slow: {results['execution_time']:.3f}s"
            
            print(f"Executed 100 tasks in {results['execution_time']:.3f}s")
            
        finally:
            await executor.stop()


@pytest.mark.performance
@pytest.mark.asyncio
class TestWorkflowPerformance:
    """Test workflow performance"""
    
    async def test_workflow_creation_performance(self, profiler):
        """Test workflow creation performance"""
        logger = AgentLogger("workflow_perf")
        builder = WorkflowBuilder(logger)
        
        profiler.start_profiling()
        
        # Create complex workflows
        workflows = []
        for i in range(50):
            workflow = (builder
                       .create_workflow(f"Perf Workflow {i}")
                       .add_task_step(f"Step 1-{i}", f"Task 1-{i}", "test")
                       .add_task_step(f"Step 2-{i}", f"Task 2-{i}", "test")
                       .add_task_step(f"Step 3-{i}", f"Task 3-{i}", "test")
                       .build())
            if workflow:
                workflows.append(workflow)
        
        profiler.end_profiling()
        results = profiler.get_results()
        
        # Performance assertions
        assert len(workflows) == 50, f"Workflow creation failed: {len(workflows)} != 50"
        assert results['execution_time'] < 1.0, f"Workflow creation too slow: {results['execution_time']:.3f}s"
        
        print(f"Created 50 workflows in {results['execution_time']:.3f}s")
    
    async def test_workflow_engine_performance(self, profiler):
        """Test workflow engine performance"""
        logger = AgentLogger("engine_perf")
        engine = WorkflowEngine(logger)
        builder = WorkflowBuilder(logger)
        
        await engine.start()
        
        try:
            # Create workflows
            workflows = []
            for i in range(20):
                workflow = (builder
                           .create_workflow(f"Engine Perf Workflow {i}")
                           .add_task_step(f"Step {i}", f"Task {i}", "perf_test")
                           .build())
                if workflow:
                    workflows.append(workflow)
            
            profiler.start_profiling()
            
            # Register all workflows
            for workflow in workflows:
                engine.register_workflow(workflow)
            
            profiler.end_profiling()
            results = profiler.get_results()
            
            # Performance assertions
            stats = engine.get_engine_stats()
            assert stats['registered_workflows'] == len(workflows)
            assert results['execution_time'] < 0.5, f"Workflow registration too slow: {results['execution_time']:.3f}s"
            
            print(f"Registered 20 workflows in {results['execution_time']:.3f}s")
            
        finally:
            await engine.stop()


@pytest.mark.performance
@pytest.mark.asyncio
class TestCommunicationPerformance:
    """Test communication performance"""
    
    async def test_message_routing_performance(self, profiler):
        """Test message routing performance"""
        logger = AgentLogger("router_perf")
        router = MessageRouter(logger)
        
        await router.start()
        
        try:
            # Create mock adapter
            class MockAdapter:
                def __init__(self):
                    from src.jobone.vision_core.communication.core import ProtocolConfig, ProtocolType
                    self.config = ProtocolConfig(protocol_type=ProtocolType.HTTP)
                
                def is_connected(self):
                    return True
                
                async def send_message(self, message, target):
                    return True
                
                def get_stats(self):
                    return {"messages_sent": 0}
            
            # Register adapter
            adapter = MockAdapter()
            router.register_adapter("perf_adapter", adapter)
            
            # Create route
            from src.jobone.vision_core.communication.core import MessageRoute, ProtocolType
            route = MessageRoute(
                source_protocol=ProtocolType.HTTP,
                target_protocol=ProtocolType.HTTP,
                source_address="*",
                target_address="*"
            )
            router.add_route("perf_route", route)
            
            # Create messages
            from src.jobone.vision_core.communication.core import CommunicationMessage, MessageType
            messages = []
            for i in range(1000):
                message = CommunicationMessage(
                    message_id=f"perf_msg_{i:04d}",
                    message_type=MessageType.TASK_REQUEST,
                    sender_id="sender",
                    recipient_id="receiver",
                    content={"index": i}
                )
                messages.append(message)
            
            profiler.start_profiling()
            
            # Route all messages
            routing_results = []
            for message in messages:
                result = await router.route_message(message)
                routing_results.append(result)
            
            profiler.end_profiling()
            results = profiler.get_results()
            
            # Performance assertions
            success_count = sum(routing_results)
            assert success_count == len(messages), f"Routing failures: {success_count} != {len(messages)}"
            assert results['execution_time'] < 2.0, f"Message routing too slow: {results['execution_time']:.3f}s"
            
            throughput = len(messages) / results['execution_time']
            print(f"Routed 1000 messages in {results['execution_time']:.3f}s ({throughput:.0f} msg/s)")
            
        finally:
            await router.stop()


@pytest.mark.performance
class TestSystemPerformance:
    """Test overall system performance"""
    
    def test_memory_usage_baseline(self, profiler):
        """Test system memory usage baseline"""
        profiler.start_profiling()
        
        # Create a complete system
        logger = AgentLogger("system_perf")
        config = AgentConfig("system_agent", "System Agent", "SystemAgent")
        
        # Create all components
        startup_mgr = StartupManager(config, logger)
        shutdown_mgr = ShutdownManager(config, logger)
        heartbeat_mgr = HeartbeatManager(config, logger)
        
        # Create tasks and workflows
        tasks = []
        for i in range(100):
            task = TaskDefinition(f"System Task {i}", "system_test")
            tasks.append(task)
        
        builder = WorkflowBuilder(logger)
        workflow = (builder
                   .create_workflow("System Workflow")
                   .add_task_step("System Step", "System Task", "system")
                   .build())
        
        profiler.end_profiling()
        results = profiler.get_results()
        
        # Memory usage should be reasonable
        assert results['peak_memory_mb'] < 100, f"System memory usage too high: {results['peak_memory_mb']:.1f}MB"
        
        print(f"System baseline memory usage: {results['peak_memory_mb']:.1f}MB")
    
    def test_concurrent_operations_performance(self, profiler):
        """Test concurrent operations performance"""
        import concurrent.futures
        
        def create_agent_components():
            config = AgentConfig("concurrent_agent", "Concurrent Agent", "ConcurrentAgent")
            logger = AgentLogger("concurrent_test")
            startup_mgr = StartupManager(config, logger)
            return startup_mgr.execute_startup()
        
        profiler.start_profiling()
        
        # Run concurrent operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_agent_components) for _ in range(50)]
            results_list = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        profiler.end_profiling()
        results = profiler.get_results()
        
        # All operations should succeed
        assert all(results_list), f"Some concurrent operations failed: {sum(results_list)}/{len(results_list)}"
        assert results['execution_time'] < 5.0, f"Concurrent operations too slow: {results['execution_time']:.3f}s"
        
        print(f"50 concurrent operations completed in {results['execution_time']:.3f}s")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-m", "performance", "--tb=short"])
