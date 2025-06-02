#!/usr/bin/env python3
"""
Basit Test Suite - Orion Vision Core
Temel modüllerin çalışıp çalışmadığını kontrol eder
"""

import sys
import os
import traceback

# Add src path
sys.path.append('src/jobone/vision_core')

def test_basic_imports():
    """Temel import testleri"""
    print("🧪 Testing Basic Imports...")
    
    tests = [
        ("Agent Core", "agent_core", "Agent"),
        ("Agent Registry", "agent_registry", "AgentRegistry"),
        ("Task Orchestration", "task_orchestration", "TaskScheduler"),
    ]
    
    results = []
    for name, module, class_name in tests:
        try:
            mod = __import__(module)
            cls = getattr(mod, class_name)
            print(f"✅ {name}: {class_name} imported successfully")
            results.append(True)
        except Exception as e:
            print(f"❌ {name}: Failed - {e}")
            results.append(False)
    
    return results

def test_agent_creation():
    """Agent oluşturma testi"""
    print("\n🤖 Testing Agent Creation...")
    
    try:
        from agent_core import Agent, AgentConfig, create_agent_config
        
        # Test config creation
        config = create_agent_config("test_agent", "Test Agent", "test")
        print("✅ Agent config created successfully")
        
        # Test agent class (abstract, so we'll create a simple implementation)
        class TestAgent(Agent):
            def initialize(self):
                return True
            
            def run(self):
                pass
            
            def cleanup(self):
                pass
        
        # Create agent
        agent = TestAgent(config)
        print("✅ Test agent created successfully")
        print(f"✅ Agent ID: {agent.agent_id}")
        print(f"✅ Agent Status: {agent.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        traceback.print_exc()
        return False

def test_task_orchestration():
    """Task orchestration testi"""
    print("\n📋 Testing Task Orchestration...")
    
    try:
        from task_orchestration import TaskScheduler, TaskDefinition
        
        # Create scheduler
        scheduler = TaskScheduler()
        print("✅ Task scheduler created successfully")
        
        # Create task definition
        task_def = TaskDefinition(
            task_id="test_task",
            task_name="Test Task",
            description="A test task",
            task_type="test"
        )
        print("✅ Task definition created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Task orchestration failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Dosya yapısı testi"""
    print("\n📁 Testing File Structure...")
    
    important_files = [
        "src/jobone/vision_core/agent_core.py",
        "src/jobone/vision_core/agent_registry.py",
        "src/jobone/vision_core/task_orchestration.py",
        "src/jobone/vision_core/llm/llm_api_manager.py",
        "src/jobone/vision_core/gui/gui_framework.py",
        "docker/Dockerfile",
        "deployment/kubernetes/deployment.yaml",
        "security/zero-trust/zero-trust-policies.yaml"
    ]
    
    results = []
    for file_path in important_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - EXISTS")
            results.append(True)
        else:
            print(f"❌ {file_path} - MISSING")
            results.append(False)
    
    return results

def main():
    """Ana test fonksiyonu"""
    print("🚀 ORION VISION CORE - SIMPLE TEST SUITE")
    print("=" * 50)
    
    all_results = []
    
    # Test 1: Basic Imports
    import_results = test_basic_imports()
    all_results.extend(import_results)
    
    # Test 2: Agent Creation
    agent_result = test_agent_creation()
    all_results.append(agent_result)
    
    # Test 3: Task Orchestration
    task_result = test_task_orchestration()
    all_results.append(task_result)
    
    # Test 4: File Structure
    file_results = test_file_structure()
    all_results.extend(file_results)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(all_results)
    passed_tests = sum(all_results)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 OVERALL STATUS: EXCELLENT")
    elif success_rate >= 60:
        print("✅ OVERALL STATUS: GOOD")
    elif success_rate >= 40:
        print("⚠️ OVERALL STATUS: NEEDS IMPROVEMENT")
    else:
        print("❌ OVERALL STATUS: CRITICAL ISSUES")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
