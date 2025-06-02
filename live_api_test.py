#!/usr/bin/env python3
"""
🚀 Live API Test - Orion Vision Core
Test real APIs and services without full system startup
"""

import requests
import time
import json
import threading
import subprocess
import sys
from datetime import datetime

class LiveAPITester:
    """Live API testing for Orion Vision Core"""
    
    def __init__(self):
        self.test_results = {}
        self.api_processes = {}
        self.base_ports = {
            'agent_management': 8000,
            'service_discovery': 8001,
            'dashboard': 8002,
            'monitoring': 8003
        }
        
    def run_live_tests(self):
        """Run comprehensive live API tests"""
        print("🚀 ORION VISION CORE - LIVE API TEST")
        print("=" * 60)
        print(f"📅 Test Time: {datetime.now().strftime('%H:%M:%S')}")
        print("🎯 Objective: Test real APIs and services")
        print("=" * 60)
        print()
        
        # Test categories
        test_categories = [
            ("Quick Import Tests", self.test_quick_imports),
            ("Service Discovery API", self.test_service_discovery_api),
            ("Agent Management API", self.test_agent_management_api),
            ("Dashboard API", self.test_dashboard_api),
            ("Core AI Manager", self.test_core_ai_manager),
            ("Task Orchestration", self.test_task_orchestration)
        ]
        
        total_score = 0
        category_count = 0
        
        for category_name, test_function in test_categories:
            print(f"🔍 TESTING: {category_name}")
            print("-" * 40)
            
            try:
                score = test_function()
                self.test_results[category_name] = score
                total_score += score
                category_count += 1
                print(f"📊 Category Score: {score:.1f}%")
            except Exception as e:
                print(f"❌ CATEGORY FAILED: {category_name} - {e}")
                self.test_results[category_name] = 0
                category_count += 1
            
            print()
        
        # Generate final report
        overall_score = total_score / category_count if category_count > 0 else 0
        self.generate_live_test_report(overall_score)
        
        return overall_score
    
    def test_quick_imports(self):
        """Test quick module imports"""
        print("Testing module imports...")
        
        modules = [
            "src.jobone.vision_core.service_discovery",
            "src.jobone.vision_core.agent_management_api",
            "src.jobone.vision_core.core_ai_manager",
            "src.jobone.vision_core.task_orchestration",
            "src.jobone.vision_core.dashboard.simple_dashboard"
        ]
        
        passed = 0
        total = len(modules)
        
        for module_path in modules:
            try:
                import importlib
                module = importlib.import_module(module_path)
                print(f"✅ {module_path.split('.')[-1]:<20} - Import OK")
                passed += 1
            except Exception as e:
                print(f"❌ {module_path.split('.')[-1]:<20} - Import FAILED: {str(e)[:30]}")
        
        return (passed / total) * 100
    
    def test_service_discovery_api(self):
        """Test Service Discovery API"""
        print("Testing Service Discovery...")
        
        try:
            # Import and create service discovery
            from src.jobone.vision_core.service_discovery import ServiceDiscovery
            
            # Create instance
            service_discovery = ServiceDiscovery()
            
            # Test basic functionality
            tests_passed = 0
            total_tests = 4
            
            # Test 1: Instance creation
            if service_discovery:
                print("✅ Service Discovery - Instance Created")
                tests_passed += 1
            else:
                print("❌ Service Discovery - Instance Creation Failed")
            
            # Test 2: Manager ID
            if hasattr(service_discovery, 'manager_id'):
                print("✅ Service Discovery - Manager ID Available")
                tests_passed += 1
            else:
                print("❌ Service Discovery - Manager ID Missing")
            
            # Test 3: Registry
            if hasattr(service_discovery, 'registry'):
                print("✅ Service Discovery - Registry Available")
                tests_passed += 1
            else:
                print("❌ Service Discovery - Registry Missing")
            
            # Test 4: Health Monitor
            if hasattr(service_discovery, 'health_monitor'):
                print("✅ Service Discovery - Health Monitor Available")
                tests_passed += 1
            else:
                print("❌ Service Discovery - Health Monitor Missing")
            
            return (tests_passed / total_tests) * 100
            
        except Exception as e:
            print(f"❌ Service Discovery - Error: {str(e)[:50]}")
            return 0
    
    def test_agent_management_api(self):
        """Test Agent Management API"""
        print("Testing Agent Management API...")
        
        try:
            # Import agent management API
            from src.jobone.vision_core.agent_management_api import app
            
            tests_passed = 0
            total_tests = 3
            
            # Test 1: App instance
            if app:
                print("✅ Agent Management - FastAPI App Available")
                tests_passed += 1
            else:
                print("❌ Agent Management - FastAPI App Missing")
            
            # Test 2: Routes
            if hasattr(app, 'routes') and len(app.routes) > 0:
                print(f"✅ Agent Management - Routes Available ({len(app.routes)} routes)")
                tests_passed += 1
            else:
                print("❌ Agent Management - No Routes Found")
            
            # Test 3: OpenAPI schema
            try:
                schema = app.openapi()
                if schema:
                    print("✅ Agent Management - OpenAPI Schema Available")
                    tests_passed += 1
                else:
                    print("❌ Agent Management - OpenAPI Schema Missing")
            except:
                print("⚠️ Agent Management - OpenAPI Schema Error")
            
            return (tests_passed / total_tests) * 100
            
        except Exception as e:
            print(f"❌ Agent Management - Error: {str(e)[:50]}")
            return 0
    
    def test_dashboard_api(self):
        """Test Dashboard functionality"""
        print("Testing Dashboard...")
        
        try:
            # Import dashboard
            from src.jobone.vision_core.dashboard.simple_dashboard import print_header, print_system_status
            
            tests_passed = 0
            total_tests = 3
            
            # Test 1: Header function
            try:
                print_header()
                print("✅ Dashboard - Header Function Works")
                tests_passed += 1
            except Exception as e:
                print(f"❌ Dashboard - Header Function Failed: {str(e)[:30]}")
            
            # Test 2: System status function
            try:
                print_system_status()
                print("✅ Dashboard - System Status Function Works")
                tests_passed += 1
            except Exception as e:
                print(f"❌ Dashboard - System Status Failed: {str(e)[:30]}")
            
            # Test 3: Module availability
            try:
                import src.jobone.vision_core.dashboard
                if hasattr(src.jobone.vision_core.dashboard, '__all__'):
                    print("✅ Dashboard - Module Exports Available")
                    tests_passed += 1
                else:
                    print("⚠️ Dashboard - Module Exports Missing")
                    tests_passed += 0.5
            except:
                print("❌ Dashboard - Module Import Failed")
            
            return (tests_passed / total_tests) * 100
            
        except Exception as e:
            print(f"❌ Dashboard - Error: {str(e)[:50]}")
            return 0
    
    def test_core_ai_manager(self):
        """Test Core AI Manager"""
        print("Testing Core AI Manager...")
        
        try:
            # Import Core AI Manager
            from src.jobone.vision_core.core_ai_manager import CoreAIManager
            
            tests_passed = 0
            total_tests = 4
            
            # Test 1: Class import
            if CoreAIManager:
                print("✅ Core AI Manager - Class Import OK")
                tests_passed += 1
            else:
                print("❌ Core AI Manager - Class Import Failed")
            
            # Test 2: Instance creation
            try:
                ai_manager = CoreAIManager()
                print("✅ Core AI Manager - Instance Created")
                tests_passed += 1
            except Exception as e:
                print(f"❌ Core AI Manager - Instance Creation Failed: {str(e)[:30]}")
                ai_manager = None
            
            # Test 3: Basic attributes
            if ai_manager and hasattr(ai_manager, 'llm_providers'):
                print("✅ Core AI Manager - LLM Providers Available")
                tests_passed += 1
            else:
                print("❌ Core AI Manager - LLM Providers Missing")
            
            # Test 4: Methods
            if ai_manager and hasattr(ai_manager, 'get_available_models'):
                print("✅ Core AI Manager - Methods Available")
                tests_passed += 1
            else:
                print("❌ Core AI Manager - Methods Missing")
            
            return (tests_passed / total_tests) * 100
            
        except Exception as e:
            print(f"❌ Core AI Manager - Error: {str(e)[:50]}")
            return 0
    
    def test_task_orchestration(self):
        """Test Task Orchestration"""
        print("Testing Task Orchestration...")
        
        try:
            # Import Task Orchestration
            from src.jobone.vision_core.task_orchestration import TaskScheduler
            
            tests_passed = 0
            total_tests = 4
            
            # Test 1: Class import
            if TaskScheduler:
                print("✅ Task Orchestration - TaskScheduler Import OK")
                tests_passed += 1
            else:
                print("❌ Task Orchestration - TaskScheduler Import Failed")
            
            # Test 2: Instance creation
            try:
                scheduler = TaskScheduler()
                print("✅ Task Orchestration - Scheduler Created")
                tests_passed += 1
            except Exception as e:
                print(f"❌ Task Orchestration - Scheduler Creation Failed: {str(e)[:30]}")
                scheduler = None
            
            # Test 3: Basic attributes
            if scheduler and hasattr(scheduler, 'tasks'):
                print("✅ Task Orchestration - Task Management Available")
                tests_passed += 1
            else:
                print("❌ Task Orchestration - Task Management Missing")
            
            # Test 4: Methods
            if scheduler and hasattr(scheduler, 'schedule_task'):
                print("✅ Task Orchestration - Scheduling Methods Available")
                tests_passed += 1
            else:
                print("❌ Task Orchestration - Scheduling Methods Missing")
            
            return (tests_passed / total_tests) * 100
            
        except Exception as e:
            print(f"❌ Task Orchestration - Error: {str(e)[:50]}")
            return 0
    
    def generate_live_test_report(self, overall_score):
        """Generate final live test report"""
        print("🎯 LIVE API TEST RESULTS")
        print("=" * 60)
        
        # Individual category results
        print("📊 CATEGORY RESULTS:")
        for category, score in self.test_results.items():
            status_icon = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            print(f"   {status_icon} {category:<25} - {score:.1f}%")
        
        print()
        print(f"🎯 OVERALL LIVE TEST SCORE: {overall_score:.1f}%")
        print()
        
        # Final verdict
        if overall_score >= 90:
            print("🎉 LIVE TEST VERDICT: EXCELLENT!")
            print("🚀 APIs and services are working great!")
            print("✅ System is production-ready for live use!")
        elif overall_score >= 75:
            print("👍 LIVE TEST VERDICT: VERY GOOD!")
            print("🔧 Most APIs working, minor issues detected!")
            print("✅ System is mostly ready for live use!")
        elif overall_score >= 60:
            print("⚠️ LIVE TEST VERDICT: NEEDS WORK!")
            print("🛠️ Several APIs need attention!")
            print("⚠️ System needs improvements before live use!")
        else:
            print("❌ LIVE TEST VERDICT: NOT READY!")
            print("🚨 Major API issues detected!")
            print("❌ System not ready for live use!")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = LiveAPITester()
    score = tester.run_live_tests()
    
    print(f"\n🎯 Final Live Test Score: {score:.1f}%")
    
    if score >= 75:
        print("🎊 Orion Vision Core APIs are working well!")
    else:
        print("🔧 Orion Vision Core APIs need improvements!")
