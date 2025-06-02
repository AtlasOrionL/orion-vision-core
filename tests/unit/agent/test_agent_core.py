"""
Unit Tests for Agent Core Modules

This module tests agent core functionality including configuration, logging, and lifecycle.
Part of Sprint 9.1.1.1 comprehensive testing suite.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch

from src.jobone.vision_core.agent.core import (
    AgentConfig, AgentLogger, AgentStatus, AgentPriority,
    get_status_description, get_priority_description
)
from src.jobone.vision_core.agent.lifecycle import (
    StartupManager, ShutdownManager, HeartbeatManager
)


class TestAgentStatus:
    """Test agent status enumeration"""
    
    def test_agent_status_values(self):
        """Test agent status enum values"""
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.ERROR.value == "error"
    
    def test_agent_priority_values(self):
        """Test agent priority enum values"""
        assert AgentPriority.LOW.value == 1
        assert AgentPriority.NORMAL.value == 2
        assert AgentPriority.CRITICAL.value == 4
    
    def test_status_description(self):
        """Test status description function"""
        desc = get_status_description(AgentStatus.RUNNING)
        assert "actively running" in desc.lower()
    
    def test_priority_description(self):
        """Test priority description function"""
        desc = get_priority_description(AgentPriority.HIGH)
        assert "high priority" in desc.lower()


class TestAgentConfig:
    """Test agent configuration"""
    
    def test_valid_config_creation(self, sample_agent_config, test_assertions):
        """Test creating valid agent configuration"""
        test_assertions.assert_agent_config_valid(sample_agent_config)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        config = AgentConfig("test_001", "Test", "TestAgent")
        assert config.validate()
        
        # Invalid configs
        with pytest.raises(ValueError):
            AgentConfig("", "Test", "TestAgent")  # Empty agent_id
        
        with pytest.raises(ValueError):
            AgentConfig("test_001", "", "TestAgent")  # Empty agent_name
        
        with pytest.raises(ValueError):
            AgentConfig("test_001", "Test", "")  # Empty agent_type
    
    def test_config_serialization(self, sample_agent_config):
        """Test configuration serialization"""
        config_dict = sample_agent_config.to_dict()
        
        assert config_dict['agent_id'] == sample_agent_config.agent_id
        assert config_dict['agent_name'] == sample_agent_config.agent_name
        assert config_dict['priority'] == sample_agent_config.priority.value
        
        # Test deserialization
        restored_config = AgentConfig.from_dict(config_dict)
        assert restored_config.agent_id == sample_agent_config.agent_id
        assert restored_config.priority == sample_agent_config.priority
    
    def test_config_defaults(self):
        """Test configuration default values"""
        config = AgentConfig("test", "Test", "TestAgent")
        
        assert config.priority == AgentPriority.NORMAL
        assert config.log_level == "INFO"
        assert config.heartbeat_interval == 5.0
        assert config.max_retries == 3
        assert config.timeout == 30.0
        assert config.auto_restart is True


class TestAgentLogger:
    """Test agent logger"""
    
    def test_logger_creation(self):
        """Test logger creation"""
        logger = AgentLogger("test_agent")
        assert logger.agent_id == "test_agent"
        assert logger.log_level == "INFO"
    
    def test_structured_logging(self, test_logger, capsys):
        """Test structured logging output"""
        test_logger.info("Test message", status="testing", module="unit_test")
        
        # Note: In real implementation, we'd capture the actual log output
        # For now, we just verify the method doesn't raise exceptions
        assert True
    
    def test_log_levels(self, test_logger):
        """Test different log levels"""
        # Test all log levels
        test_logger.debug("Debug message", test_data="debug")
        test_logger.info("Info message", test_data="info")
        test_logger.warning("Warning message", test_data="warning")
        test_logger.error("Error message", test_data="error")
        test_logger.critical("Critical message", test_data="critical")
        
        # Verify no exceptions raised
        assert True


class TestStartupManager:
    """Test startup manager"""
    
    def test_startup_manager_creation(self, sample_agent_config, test_logger):
        """Test startup manager creation"""
        manager = StartupManager(sample_agent_config, test_logger)
        assert manager.config == sample_agent_config
        assert manager.logger == test_logger
        assert len(manager.startup_callbacks) == 0
    
    def test_add_startup_callback(self, sample_agent_config, test_logger):
        """Test adding startup callbacks"""
        manager = StartupManager(sample_agent_config, test_logger)
        
        def test_callback():
            pass
        
        manager.add_startup_callback(test_callback, priority=5)
        assert len(manager.startup_callbacks) == 1
        assert manager.startup_callbacks[0][0] == 5  # Priority
        assert manager.startup_callbacks[0][1] == test_callback
    
    def test_startup_execution(self, sample_agent_config, test_logger):
        """Test startup execution"""
        manager = StartupManager(sample_agent_config, test_logger)
        
        callback_executed = []
        
        def test_callback():
            callback_executed.append(True)
        
        manager.add_startup_callback(test_callback)
        result = manager.execute_startup()
        
        assert result is True
        assert manager.startup_success is True
        assert manager.startup_time is not None
        assert len(callback_executed) == 1
    
    def test_startup_failure(self, sample_agent_config, test_logger):
        """Test startup failure handling"""
        manager = StartupManager(sample_agent_config, test_logger)
        
        def failing_callback():
            raise Exception("Test failure")
        
        manager.add_startup_callback(failing_callback)
        result = manager.execute_startup()
        
        assert result is False
        assert manager.startup_success is False
        assert len(manager.startup_errors) > 0
    
    def test_startup_stats(self, sample_agent_config, test_logger):
        """Test startup statistics"""
        manager = StartupManager(sample_agent_config, test_logger)
        manager.execute_startup()
        
        stats = manager.get_startup_stats()
        assert 'startup_time' in stats
        assert 'startup_success' in stats
        assert 'callbacks_count' in stats
        assert 'errors_count' in stats


class TestShutdownManager:
    """Test shutdown manager"""
    
    def test_shutdown_manager_creation(self, sample_agent_config, test_logger):
        """Test shutdown manager creation"""
        manager = ShutdownManager(sample_agent_config, test_logger)
        assert manager.config == sample_agent_config
        assert manager.logger == test_logger
    
    def test_shutdown_execution(self, sample_agent_config, test_logger):
        """Test shutdown execution"""
        manager = ShutdownManager(sample_agent_config, test_logger)
        
        callback_executed = []
        
        def test_callback():
            callback_executed.append(True)
        
        manager.add_shutdown_callback(test_callback)
        result = manager.execute_shutdown(timeout=5.0)
        
        assert result is True
        assert manager.shutdown_success is True
        assert len(callback_executed) == 1
    
    def test_shutdown_timeout(self, sample_agent_config, test_logger):
        """Test shutdown with timeout"""
        manager = ShutdownManager(sample_agent_config, test_logger)
        
        def slow_callback():
            time.sleep(2.0)  # Simulate slow shutdown
        
        manager.add_shutdown_callback(slow_callback)
        
        start_time = time.time()
        result = manager.execute_shutdown(timeout=0.1)  # Very short timeout
        end_time = time.time()
        
        # Should complete quickly due to timeout
        assert (end_time - start_time) < 1.0
    
    def test_force_shutdown(self, sample_agent_config, test_logger):
        """Test force shutdown"""
        manager = ShutdownManager(sample_agent_config, test_logger)
        
        def failing_callback():
            raise Exception("Shutdown error")
        
        manager.add_shutdown_callback(failing_callback)
        result = manager.execute_shutdown(force=True)
        
        # Should succeed even with failing callback when forced
        assert result is True
        assert manager.force_shutdown is True


class TestHeartbeatManager:
    """Test heartbeat manager"""
    
    def test_heartbeat_manager_creation(self, sample_agent_config, test_logger):
        """Test heartbeat manager creation"""
        manager = HeartbeatManager(sample_agent_config, test_logger)
        assert manager.config == sample_agent_config
        assert manager.logger == test_logger
        assert manager.heartbeat_count == 0
    
    def test_heartbeat_lifecycle(self, sample_agent_config, test_logger):
        """Test heartbeat start/stop lifecycle"""
        manager = HeartbeatManager(sample_agent_config, test_logger)
        
        # Start heartbeat
        manager.start_heartbeat()
        assert manager.is_heartbeat_alive()
        
        # Let it run briefly
        time.sleep(0.5)
        
        # Stop heartbeat
        manager.stop_heartbeat()
        assert not manager.is_heartbeat_alive()
    
    def test_health_callbacks(self, sample_agent_config, test_logger):
        """Test health check callbacks"""
        manager = HeartbeatManager(sample_agent_config, test_logger)
        
        health_checks = []
        
        def health_callback():
            health_checks.append(True)
            return True
        
        manager.add_health_callback(health_callback)
        
        # Start heartbeat and let it run
        manager.start_heartbeat()
        time.sleep(1.5)  # Let at least one heartbeat occur
        manager.stop_heartbeat()
        
        # Health callback should have been called
        assert len(health_checks) > 0
    
    def test_heartbeat_stats(self, sample_agent_config, test_logger):
        """Test heartbeat statistics"""
        manager = HeartbeatManager(sample_agent_config, test_logger)
        
        manager.start_heartbeat()
        time.sleep(1.5)  # Let some heartbeats occur
        manager.stop_heartbeat()
        
        stats = manager.get_heartbeat_stats()
        assert 'heartbeat_count' in stats
        assert 'missed_heartbeats' in stats
        assert 'is_healthy' in stats
        assert 'is_alive' in stats
        assert stats['heartbeat_count'] > 0


class TestAgentIntegration:
    """Test agent component integration"""
    
    def test_full_agent_lifecycle(self, sample_agent_config, test_logger):
        """Test complete agent lifecycle"""
        # Create managers
        startup_mgr = StartupManager(sample_agent_config, test_logger)
        shutdown_mgr = ShutdownManager(sample_agent_config, test_logger)
        heartbeat_mgr = HeartbeatManager(sample_agent_config, test_logger)
        
        # Test startup
        assert startup_mgr.execute_startup()
        
        # Test heartbeat
        heartbeat_mgr.start_heartbeat()
        time.sleep(0.5)
        assert heartbeat_mgr.is_heartbeat_alive()
        
        # Test shutdown
        heartbeat_mgr.stop_heartbeat()
        assert shutdown_mgr.execute_shutdown()
        
        # Verify final state
        assert startup_mgr.startup_success
        assert shutdown_mgr.shutdown_success
        assert not heartbeat_mgr.is_heartbeat_alive()
    
    def test_agent_configuration_integration(self, test_data_generator):
        """Test multiple agent configurations"""
        configs = test_data_generator.generate_agent_configs(5)
        
        for config in configs:
            assert config.validate()
            
            # Test serialization round-trip
            config_dict = config.to_dict()
            restored = AgentConfig.from_dict(config_dict)
            assert restored.agent_id == config.agent_id
            assert restored.priority == config.priority
