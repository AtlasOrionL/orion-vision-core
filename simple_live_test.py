#!/usr/bin/env python3
"""
🚀 Simple Live Test - Orion Vision Core
Basic functionality test without server startup
"""

def test_core_functionality():
    """Test core functionality without starting servers"""
    print("🚀 ORION VISION CORE - SIMPLE LIVE TEST")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Service Discovery
    print("🔍 Test 1: Service Discovery")
    try:
        from src.jobone.vision_core.service_discovery import ServiceDiscovery
        sd = ServiceDiscovery()
        print(f"✅ Service Discovery OK - Manager: {sd.manager_id[:15]}...")
        results['service_discovery'] = True
    except Exception as e:
        print(f"❌ Service Discovery FAILED: {str(e)[:40]}")
        results['service_discovery'] = False
    
    # Test 2: Agent Management API Structure
    print("\n🔍 Test 2: Agent Management API")
    try:
        from src.jobone.vision_core.agent_management_api import app
        routes = len(app.routes)
        print(f"✅ Agent Management API OK - {routes} routes")
        results['agent_api'] = True
    except Exception as e:
        print(f"❌ Agent Management API FAILED: {str(e)[:40]}")
        results['agent_api'] = False
    
    # Test 3: Core AI Manager
    print("\n🔍 Test 3: Core AI Manager")
    try:
        from src.jobone.vision_core.core_ai_manager import CoreAIManager
        ai = CoreAIManager()
        print(f"✅ Core AI Manager OK - State: {ai.state}")
        results['ai_manager'] = True
    except Exception as e:
        print(f"❌ Core AI Manager FAILED: {str(e)[:40]}")
        results['ai_manager'] = False
    
    # Test 4: Task Orchestration
    print("\n🔍 Test 4: Task Orchestration")
    try:
        from src.jobone.vision_core.task_orchestration import TaskScheduler
        ts = TaskScheduler()
        print("✅ Task Orchestration OK")
        results['task_orchestration'] = True
    except Exception as e:
        print(f"❌ Task Orchestration FAILED: {str(e)[:40]}")
        results['task_orchestration'] = False
    
    # Test 5: Dashboard
    print("\n🔍 Test 5: Dashboard")
    try:
        from src.jobone.vision_core.dashboard.simple_dashboard import print_header
        print("✅ Dashboard OK")
        results['dashboard'] = True
    except Exception as e:
        print(f"❌ Dashboard FAILED: {str(e)[:40]}")
        results['dashboard'] = False
    
    # Test 6: GUI Module
    print("\n🔍 Test 6: GUI Module")
    try:
        from src.jobone.vision_core.gui import GUIManager
        print("✅ GUI Module OK")
        results['gui'] = True
    except Exception as e:
        print(f"❌ GUI Module FAILED: {str(e)[:40]}")
        results['gui'] = False
    
    # Test 7: Mobile Module
    print("\n🔍 Test 7: Mobile Module")
    try:
        from src.jobone.vision_core.mobile import MobileAppFoundation
        print("✅ Mobile Module OK")
        results['mobile'] = True
    except Exception as e:
        print(f"❌ Mobile Module FAILED: {str(e)[:40]}")
        results['mobile'] = False
    
    # Test 8: Cloud Module
    print("\n🔍 Test 8: Cloud Module")
    try:
        from src.jobone.vision_core.cloud import CloudStorageManager
        print("✅ Cloud Module OK")
        results['cloud'] = True
    except Exception as e:
        print(f"❌ Cloud Module FAILED: {str(e)[:40]}")
        results['cloud'] = False
    
    # Calculate results
    total_tests = len(results)
    passed_tests = sum(results.values())
    success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 50)
    print("🎯 LIVE TEST RESULTS")
    print("=" * 50)
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 EXCELLENT! Core systems are working great!")
        print("🚀 Orion Vision Core is live and functional!")
    elif success_rate >= 75:
        print("\n👍 VERY GOOD! Most systems are working!")
        print("🔧 Minor issues detected, mostly functional!")
    elif success_rate >= 50:
        print("\n⚠️ MODERATE! Some systems working!")
        print("🛠️ Several issues need attention!")
    else:
        print("\n❌ POOR! Major issues detected!")
        print("🚨 System needs significant work!")
    
    print("=" * 50)
    return success_rate

if __name__ == "__main__":
    score = test_core_functionality()
    print(f"\nFinal Live Test Score: {score:.1f}%")
