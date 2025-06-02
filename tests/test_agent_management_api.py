#!/usr/bin/env python3
"""
Agent Management API Tests - Atlas Prompt 3.1.2
Orion Vision Core - Agent Yönetim API'si Testleri

Bu script, agent_management_api.py modülünün unit testlerini içerir.
"""

import unittest
import sys
import os
import time
import tempfile
import shutil
import threading
from unittest.mock import Mock, patch, MagicMock

# Test modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))

# Mock FastAPI dependencies
sys.modules['fastapi'] = MagicMock()
sys.modules['fastapi.middleware'] = MagicMock()
sys.modules['fastapi.middleware.cors'] = MagicMock()
sys.modules['fastapi.responses'] = MagicMock()
sys.modules['fastapi.staticfiles'] = MagicMock()
sys.modules['fastapi.templating'] = MagicMock()
sys.modules['uvicorn'] = MagicMock()
sys.modules['pydantic'] = MagicMock()

# Import after mocking
from agent_management_api import (
    AgentCreateRequest, AgentActionRequest, ModuleLoadRequest,
    AgentResponse, ModuleResponse, APIResponse
)


class TestAgentManagementAPI(unittest.TestCase):
    """Agent Management API testleri"""
    
    def setUp(self):
        """Her test öncesi kurulum"""
        # Mock loader ve registry
        self.mock_loader = Mock()
        self.mock_registry = Mock()
        
        # Mock agent
        self.mock_agent = Mock()
        self.mock_agent.agent_id = "test_agent_001"
        self.mock_agent.agent_name = "Test Agent"
        self.mock_agent.agent_type = "test_agent"
        self.mock_agent.status.value = "running"
        self.mock_agent.is_running.return_value = True
        self.mock_agent.get_status.return_value = {
            'agent_id': 'test_agent_001',
            'agent_name': 'Test Agent',
            'agent_type': 'test_agent',
            'status': 'running',
            'uptime': 10.5,
            'is_healthy': True,
            'capabilities': ['test_capability'],
            'stats': {'tasks_completed': 5}
        }
        
        # Mock module info
        self.mock_module_info = Mock()
        self.mock_module_info.module_name = "test_module"
        self.mock_module_info.module_path = "/path/to/test_module.py"
        self.mock_module_info.is_loaded = True
        self.mock_module_info.agent_class_name = "TestAgent"
        self.mock_module_info.last_modified = time.time()
        self.mock_module_info.load_time = time.time()
        self.mock_module_info.error_message = None
    
    def test_pydantic_models(self):
        """Pydantic model testleri"""
        # AgentCreateRequest
        create_request = AgentCreateRequest(
            module_name="test_module",
            agent_id="test_agent_001",
            auto_start=True
        )
        self.assertEqual(create_request.module_name, "test_module")
        self.assertEqual(create_request.agent_id, "test_agent_001")
        self.assertTrue(create_request.auto_start)
        
        # AgentActionRequest
        action_request = AgentActionRequest(agent_id="test_agent_001")
        self.assertEqual(action_request.agent_id, "test_agent_001")
        
        # ModuleLoadRequest
        load_request = ModuleLoadRequest(module_name="test_module")
        self.assertEqual(load_request.module_name, "test_module")
        
        # AgentResponse
        agent_response = AgentResponse(
            agent_id="test_agent_001",
            agent_name="Test Agent",
            agent_type="test_agent",
            status="running",
            uptime=10.5,
            is_healthy=True,
            capabilities=["test_capability"],
            stats={"tasks_completed": 5}
        )
        self.assertEqual(agent_response.agent_id, "test_agent_001")
        self.assertEqual(agent_response.status, "running")
        self.assertTrue(agent_response.is_healthy)
        
        # ModuleResponse
        module_response = ModuleResponse(
            module_name="test_module",
            module_path="/path/to/test_module.py",
            is_loaded=True,
            agent_class_name="TestAgent"
        )
        self.assertEqual(module_response.module_name, "test_module")
        self.assertTrue(module_response.is_loaded)
        
        # APIResponse
        api_response = APIResponse(
            success=True,
            message="Test successful",
            data={"test": "data"}
        )
        self.assertTrue(api_response.success)
        self.assertEqual(api_response.message, "Test successful")
        self.assertEqual(api_response.data["test"], "data")
    
    def test_api_response_creation(self):
        """API response oluşturma testleri"""
        # Başarılı response
        success_response = APIResponse(
            success=True,
            message="Operation successful"
        )
        self.assertTrue(success_response.success)
        self.assertEqual(success_response.message, "Operation successful")
        self.assertIsNone(success_response.data)
        self.assertIsInstance(success_response.timestamp, float)
        
        # Hata response
        error_response = APIResponse(
            success=False,
            message="Operation failed",
            data={"error_code": 500}
        )
        self.assertFalse(error_response.success)
        self.assertEqual(error_response.message, "Operation failed")
        self.assertEqual(error_response.data["error_code"], 500)
    
    def test_agent_response_validation(self):
        """Agent response validasyon testleri"""
        # Geçerli agent response
        valid_response = AgentResponse(
            agent_id="valid_agent",
            agent_name="Valid Agent",
            agent_type="valid_type",
            status="running",
            uptime=100.0,
            is_healthy=True,
            capabilities=["cap1", "cap2"],
            stats={"metric1": 10, "metric2": 20}
        )
        
        self.assertEqual(valid_response.agent_id, "valid_agent")
        self.assertEqual(len(valid_response.capabilities), 2)
        self.assertEqual(valid_response.stats["metric1"], 10)
    
    def test_module_response_validation(self):
        """Module response validasyon testleri"""
        # Yüklü modül response
        loaded_module = ModuleResponse(
            module_name="loaded_module",
            module_path="/path/to/loaded_module.py",
            is_loaded=True,
            agent_class_name="LoadedAgent",
            last_modified=time.time(),
            load_time=time.time()
        )
        
        self.assertTrue(loaded_module.is_loaded)
        self.assertEqual(loaded_module.agent_class_name, "LoadedAgent")
        self.assertIsNotNone(loaded_module.last_modified)
        
        # Yüklenmemiş modül response
        unloaded_module = ModuleResponse(
            module_name="unloaded_module",
            module_path="/path/to/unloaded_module.py",
            is_loaded=False,
            agent_class_name="",
            error_message="Module not found"
        )
        
        self.assertFalse(unloaded_module.is_loaded)
        self.assertEqual(unloaded_module.agent_class_name, "")
        self.assertEqual(unloaded_module.error_message, "Module not found")
    
    def test_request_validation(self):
        """Request validasyon testleri"""
        # Agent create request - gerekli alanlar
        try:
            AgentCreateRequest(
                module_name="test_module",
                agent_id="test_agent"
            )
        except Exception as e:
            self.fail(f"Valid AgentCreateRequest failed: {e}")
        
        # Module load request - gerekli alanlar
        try:
            ModuleLoadRequest(module_name="test_module")
        except Exception as e:
            self.fail(f"Valid ModuleLoadRequest failed: {e}")
        
        # Agent action request - gerekli alanlar
        try:
            AgentActionRequest(agent_id="test_agent")
        except Exception as e:
            self.fail(f"Valid AgentActionRequest failed: {e}")
    
    def test_response_serialization(self):
        """Response serialization testleri"""
        # Agent response serialization
        agent_response = AgentResponse(
            agent_id="test_agent",
            agent_name="Test Agent",
            agent_type="test",
            status="running",
            uptime=50.0,
            is_healthy=True,
            capabilities=["test"],
            stats={"count": 1}
        )
        
        # Dict'e dönüştürme (Pydantic model_dump benzeri)
        agent_dict = {
            "agent_id": agent_response.agent_id,
            "agent_name": agent_response.agent_name,
            "agent_type": agent_response.agent_type,
            "status": agent_response.status,
            "uptime": agent_response.uptime,
            "is_healthy": agent_response.is_healthy,
            "capabilities": agent_response.capabilities,
            "stats": agent_response.stats
        }
        
        self.assertEqual(agent_dict["agent_id"], "test_agent")
        self.assertEqual(agent_dict["status"], "running")
        self.assertTrue(agent_dict["is_healthy"])
    
    def test_api_response_with_data(self):
        """Data içeren API response testleri"""
        # Liste data
        list_response = APIResponse(
            success=True,
            message="List retrieved",
            data=[{"id": 1}, {"id": 2}]
        )
        
        self.assertTrue(list_response.success)
        self.assertEqual(len(list_response.data), 2)
        self.assertEqual(list_response.data[0]["id"], 1)
        
        # Dict data
        dict_response = APIResponse(
            success=True,
            message="Object retrieved",
            data={"name": "test", "value": 42}
        )
        
        self.assertTrue(dict_response.success)
        self.assertEqual(dict_response.data["name"], "test")
        self.assertEqual(dict_response.data["value"], 42)
    
    def test_error_response_handling(self):
        """Hata response işleme testleri"""
        # API hatası
        error_response = APIResponse(
            success=False,
            message="Internal server error",
            data={"error_code": 500, "details": "Database connection failed"}
        )
        
        self.assertFalse(error_response.success)
        self.assertIn("error", error_response.message.lower())
        self.assertEqual(error_response.data["error_code"], 500)
        
        # Validation hatası
        validation_error = APIResponse(
            success=False,
            message="Validation failed",
            data={"field_errors": {"agent_id": "Required field"}}
        )
        
        self.assertFalse(validation_error.success)
        self.assertIn("validation", validation_error.message.lower())
        self.assertIn("field_errors", validation_error.data)
    
    def test_timestamp_generation(self):
        """Timestamp oluşturma testleri"""
        response1 = APIResponse(success=True, message="Test 1")
        time.sleep(0.01)  # Küçük gecikme
        response2 = APIResponse(success=True, message="Test 2")
        
        # Timestamp'ler farklı olmalı
        self.assertNotEqual(response1.timestamp, response2.timestamp)
        self.assertGreater(response2.timestamp, response1.timestamp)
        
        # Timestamp yakın zamanda olmalı
        current_time = time.time()
        self.assertLess(abs(current_time - response1.timestamp), 1.0)
    
    def test_optional_fields(self):
        """Opsiyonel alan testleri"""
        # AgentCreateRequest - opsiyonel alanlar
        minimal_request = AgentCreateRequest(
            module_name="test_module",
            agent_id="test_agent"
        )
        self.assertIsNone(minimal_request.config_path)
        self.assertFalse(minimal_request.auto_start)
        
        full_request = AgentCreateRequest(
            module_name="test_module",
            agent_id="test_agent",
            config_path="/path/to/config.json",
            auto_start=True
        )
        self.assertEqual(full_request.config_path, "/path/to/config.json")
        self.assertTrue(full_request.auto_start)
        
        # ModuleResponse - opsiyonel alanlar
        minimal_module = ModuleResponse(
            module_name="test_module",
            module_path="/path/to/module.py",
            is_loaded=False,
            agent_class_name=""
        )
        self.assertIsNone(minimal_module.last_modified)
        self.assertIsNone(minimal_module.load_time)
        self.assertIsNone(minimal_module.error_message)
    
    def test_complex_data_structures(self):
        """Karmaşık veri yapısı testleri"""
        # Nested data structure
        complex_data = {
            "agents": [
                {
                    "id": "agent1",
                    "status": "running",
                    "metrics": {"cpu": 10.5, "memory": 256}
                },
                {
                    "id": "agent2", 
                    "status": "stopped",
                    "metrics": {"cpu": 0.0, "memory": 0}
                }
            ],
            "summary": {
                "total": 2,
                "running": 1,
                "stopped": 1
            }
        }
        
        response = APIResponse(
            success=True,
            message="Complex data retrieved",
            data=complex_data
        )
        
        self.assertTrue(response.success)
        self.assertEqual(len(response.data["agents"]), 2)
        self.assertEqual(response.data["summary"]["total"], 2)
        self.assertEqual(response.data["agents"][0]["metrics"]["cpu"], 10.5)


def run_api_tests():
    """Agent Management API testlerini çalıştır"""
    print("🚀 Agent Management API Tests - Atlas Prompt 3.1.2")
    print("=" * 60)
    
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test sınıfını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestAgentManagementAPI))
    
    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Testleri çalıştır
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 Tüm Agent Management API testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_api_tests()
    sys.exit(0 if success else 1)
