"""
Pytest Configuration for Orion Vision Core Tests

This module provides pytest configuration and fixtures for testing.
Part of Sprint 9.1.1.1 comprehensive testing suite.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Import test modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.jobone.vision_core.agent.core import AgentConfig, AgentLogger, AgentStatus, AgentPriority
from src.jobone.vision_core.tasks.core import TaskDefinition, TaskExecution, TaskStatus, TaskPriority
from src.jobone.vision_core.tasks.orchestration import TaskScheduler, TaskExecutor
from src.jobone.vision_core.tasks.workflow import WorkflowEngine, WorkflowBuilder
from src.jobone.vision_core.communication.core import ProtocolConfig, CommunicationMessage, ProtocolType, MessageType, MessagePriority
from src.jobone.vision_core.communication.routing import MessageRouter


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def test_logger():
    """Create test logger"""
    return AgentLogger("test_agent", "DEBUG")


@pytest.fixture
def sample_agent_config():
    """Create sample agent configuration"""
    return AgentConfig(
        agent_id="test_agent_001",
        agent_name="Test Agent",
        agent_type="TestAgent",
        priority=AgentPriority.NORMAL,
        log_level="DEBUG",
        heartbeat_interval=1.0,
        timeout=10.0
    )


@pytest.fixture
def sample_task_definition():
    """Create sample task definition"""
    return TaskDefinition(
        task_name="Test Task",
        task_type="test",
        description="A test task",
        required_capabilities=["python", "testing"],
        priority=TaskPriority.HIGH,
        timeout=30.0,
        input_data={"test_param": "test_value"}
    )


@pytest.fixture
def sample_protocol_config():
    """Create sample protocol configuration"""
    return ProtocolConfig(
        protocol_type=ProtocolType.HTTP,
        host="localhost",
        port=8080,
        timeout=10.0
    )


@pytest.fixture
def sample_communication_message():
    """Create sample communication message"""
    return CommunicationMessage(
        message_id="test_msg_001",
        message_type=MessageType.TASK_REQUEST,
        sender_id="agent_001",
        recipient_id="agent_002",
        content={"task": "test_task", "data": "test_data"},
        priority=MessagePriority.HIGH
    )


@pytest.fixture
async def task_scheduler(test_logger):
    """Create and start task scheduler"""
    scheduler = TaskScheduler(test_logger)
    await scheduler.start()
    yield scheduler
    await scheduler.stop()


@pytest.fixture
async def task_executor(test_logger):
    """Create and start task executor"""
    executor = TaskExecutor(test_logger)
    await executor.start()
    yield executor
    await executor.stop()


@pytest.fixture
async def workflow_engine(test_logger):
    """Create and start workflow engine"""
    engine = WorkflowEngine(test_logger)
    await engine.start()
    yield engine
    await engine.stop()


@pytest.fixture
def workflow_builder(test_logger):
    """Create workflow builder"""
    return WorkflowBuilder(test_logger)


@pytest.fixture
async def message_router(test_logger):
    """Create and start message router"""
    router = MessageRouter(test_logger)
    await router.start()
    yield router
    await router.stop()


@pytest.fixture
def mock_agent_data():
    """Mock agent data for testing"""
    return {
        "agent_001": {
            "capabilities": ["python", "data_processing"],
            "max_concurrent_tasks": 3,
            "status": "available"
        },
        "agent_002": {
            "capabilities": ["python", "machine_learning"],
            "max_concurrent_tasks": 2,
            "status": "available"
        },
        "agent_003": {
            "capabilities": ["javascript", "web_development"],
            "max_concurrent_tasks": 4,
            "status": "available"
        }
    }


@pytest.fixture
def performance_baseline():
    """Performance baseline metrics for testing"""
    return {
        "task_scheduling_time": 0.001,  # 1ms
        "task_execution_time": 0.1,     # 100ms
        "message_routing_time": 0.001,  # 1ms
        "workflow_execution_time": 0.5, # 500ms
        "memory_usage_mb": 50,           # 50MB
        "cpu_usage_percent": 10          # 10%
    }


# Test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "asyncio: mark test as async test"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add asyncio marker to async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
        
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add performance marker to performance tests
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)


# Test reporting hooks
def pytest_runtest_makereport(item, call):
    """Create test report"""
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    """Setup test run"""
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)


# Custom assertions
class TestAssertions:
    """Custom test assertions for Orion Vision Core"""
    
    @staticmethod
    def assert_agent_config_valid(config: AgentConfig):
        """Assert agent configuration is valid"""
        assert config.validate()
        assert config.agent_id
        assert config.agent_name
        assert config.agent_type
        assert config.heartbeat_interval > 0
        assert config.timeout > 0
        assert config.max_retries >= 0
    
    @staticmethod
    def assert_task_definition_valid(task: TaskDefinition):
        """Assert task definition is valid"""
        assert task.validate()
        assert task.task_name
        assert task.task_type
        assert task.timeout > 0
        assert task.retry_count >= 0
    
    @staticmethod
    def assert_message_valid(message: CommunicationMessage):
        """Assert communication message is valid"""
        assert message.message_id
        assert message.sender_id
        assert message.recipient_id
        assert isinstance(message.content, dict)
        assert not message.is_expired()
    
    @staticmethod
    def assert_performance_acceptable(actual: float, baseline: float, tolerance: float = 0.2):
        """Assert performance is within acceptable range"""
        max_acceptable = baseline * (1 + tolerance)
        assert actual <= max_acceptable, f"Performance degraded: {actual} > {max_acceptable}"


@pytest.fixture
def test_assertions():
    """Provide custom test assertions"""
    return TestAssertions()


# Test data generators
class TestDataGenerator:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def generate_agent_configs(count: int = 5):
        """Generate multiple agent configurations"""
        configs = []
        for i in range(count):
            config = AgentConfig(
                agent_id=f"test_agent_{i:03d}",
                agent_name=f"Test Agent {i}",
                agent_type="TestAgent",
                priority=AgentPriority.NORMAL,
                heartbeat_interval=1.0 + (i * 0.1),
                timeout=10.0 + (i * 2.0)
            )
            configs.append(config)
        return configs
    
    @staticmethod
    def generate_task_definitions(count: int = 10):
        """Generate multiple task definitions"""
        tasks = []
        for i in range(count):
            task = TaskDefinition(
                task_name=f"Test Task {i}",
                task_type="test",
                description=f"Test task number {i}",
                priority=TaskPriority(((i % 5) + 1)),
                timeout=30.0 + (i * 5.0),
                input_data={"task_index": i, "test_data": f"data_{i}"}
            )
            tasks.append(task)
        return tasks
    
    @staticmethod
    def generate_communication_messages(count: int = 20):
        """Generate multiple communication messages"""
        messages = []
        for i in range(count):
            message = CommunicationMessage(
                message_id=f"test_msg_{i:03d}",
                message_type=MessageType.TASK_REQUEST,
                sender_id=f"agent_{i % 3:03d}",
                recipient_id=f"agent_{(i + 1) % 3:03d}",
                content={"message_index": i, "test_content": f"content_{i}"},
                priority=MessagePriority(((i % 5) + 1))
            )
            messages.append(message)
        return messages


@pytest.fixture
def test_data_generator():
    """Provide test data generator"""
    return TestDataGenerator()
