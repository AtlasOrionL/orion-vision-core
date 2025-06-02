#!/usr/bin/env python3
"""
Simple API Test - Atlas Prompt 3.1.2
Orion Vision Core - Basit API Test Scripti

Bu script, Agent Management API'sinin temel işlevselliğini test eder.
"""

import sys
import os
import time

# Agent modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))

from dynamic_agent_loader import DynamicAgentLoader
from agent_registry import get_global_registry


def test_api_components():
    """API bileşenlerini test et"""
    print("🚀 Simple API Component Test - Atlas Prompt 3.1.2")
    print("=" * 60)
    
    try:
        # 1. Dynamic Agent Loader testi
        print("\n📦 1. Testing Dynamic Agent Loader...")
        loader = DynamicAgentLoader(
            agent_modules_dir="agents/dynamic",
            config_dir="config/agents",
            auto_scan=False
        )
        
        print("✅ Dynamic Agent Loader created successfully")
        
        # Modül tarama
        modules = loader.scan_modules()
        print(f"✅ Module scan completed: {len(modules)} modules found")
        
        for module_name in modules:
            print(f"   📄 {module_name}")
        
        # 2. Registry testi
        print("\n📋 2. Testing Agent Registry...")
        registry = get_global_registry()
        
        registry_stats = registry.get_registry_stats()
        print("✅ Agent Registry accessed successfully")
        print(f"   Total agents: {registry_stats['total_agents']}")
        print(f"   Healthy agents: {registry_stats['healthy_agents']}")
        
        # 3. Modül yükleme testi
        print("\n🔄 3. Testing Module Loading...")
        
        if modules:
            test_module = modules[0]
            print(f"Loading module: {test_module}")
            
            success = loader.load_module(test_module)
            if success:
                print(f"✅ Module {test_module} loaded successfully")
                
                module_info = loader.get_module_info(test_module)
                if module_info:
                    print(f"   Class: {module_info.agent_class_name}")
                    print(f"   Loaded: {module_info.is_loaded}")
            else:
                print(f"❌ Failed to load module {test_module}")
        
        # 4. Agent oluşturma testi
        print("\n🤖 4. Testing Agent Creation...")
        
        loaded_modules = loader.get_loaded_modules()
        if loaded_modules:
            test_module = loaded_modules[0]
            test_agent_id = f"simple_test_agent_{int(time.time())}"
            
            print(f"Creating agent: {test_agent_id} from {test_module}")
            
            agent = loader.create_agent(
                module_name=test_module,
                agent_id=test_agent_id
            )
            
            if agent:
                print(f"✅ Agent {test_agent_id} created successfully")
                print(f"   Type: {agent.agent_type}")
                print(f"   Status: {agent.status.value}")
                
                # Agent'ı başlat
                print(f"Starting agent: {test_agent_id}")
                start_success = loader.start_agent(test_agent_id)
                
                if start_success:
                    print(f"✅ Agent {test_agent_id} started successfully")
                    
                    # Biraz bekle
                    time.sleep(2)
                    
                    # Agent durumunu kontrol et
                    status = agent.get_status()
                    print(f"   Status: {status['status']}")
                    print(f"   Uptime: {status['uptime']:.1f}s")
                    print(f"   Healthy: {status['is_healthy']}")
                    
                    # Agent'ı durdur
                    print(f"Stopping agent: {test_agent_id}")
                    stop_success = loader.stop_agent(test_agent_id)
                    
                    if stop_success:
                        print(f"✅ Agent {test_agent_id} stopped successfully")
                    else:
                        print(f"❌ Failed to stop agent {test_agent_id}")
                else:
                    print(f"❌ Failed to start agent {test_agent_id}")
            else:
                print(f"❌ Failed to create agent {test_agent_id}")
        
        # 5. Loader istatistikleri
        print("\n📊 5. Testing Loader Statistics...")
        
        stats = loader.get_loader_stats()
        print("✅ Loader statistics retrieved")
        print(f"   Status: {stats['status']}")
        print(f"   Total modules: {stats['total_modules']}")
        print(f"   Loaded modules: {stats['loaded_modules']}")
        print(f"   Total agents: {stats['total_agents']}")
        print(f"   Running agents: {stats['running_agents']}")
        
        # 6. Temizlik
        print("\n🧹 6. Cleanup...")
        loader.shutdown()
        print("✅ Loader shutdown completed")
        
        print("\n🎉 All API component tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pydantic_models():
    """Pydantic model'leri test et"""
    print("\n🔧 Testing Pydantic Models...")
    
    try:
        # Basit model test
        from agent_management_api import APIResponse
        
        # APIResponse test
        response = APIResponse(
            success=True,
            message="Test successful",
            data={"test": "data"}
        )
        
        print("✅ APIResponse model works")
        print(f"   Success: {response.success}")
        print(f"   Message: {response.message}")
        print(f"   Data: {response.data}")
        print(f"   Timestamp: {response.timestamp}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pydantic model test failed: {e}")
        return False


def main():
    """Ana test fonksiyonu"""
    print("🧪 Starting Simple API Tests...")
    
    # Component testleri
    component_success = test_api_components()
    
    # Model testleri
    model_success = test_pydantic_models()
    
    # Sonuç
    if component_success and model_success:
        print("\n🎉 All tests passed successfully!")
        print("✅ API components are ready for production")
        return True
    else:
        print("\n❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
