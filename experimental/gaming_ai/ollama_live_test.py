#!/usr/bin/env python3
"""
🤖 Ollama Live Test - Gaming AI

Real-world testing of Gaming AI with live Ollama integration.
Tests all AI assistance features with actual LLM responses.

Author: Nexus - Quantum AI Architect
Test Type: Live Ollama Integration Test
"""

import sys
import os
import time
import logging
import asyncio
import json
from typing import Dict, List, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for Ollama testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ollama_live_test.log')
        ]
    )

async def test_ollama_connection():
    """Test basic Ollama connection"""
    print("🤖 Testing Ollama Connection...")
    
    try:
        import requests
        
        # Test Ollama API
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"  ✅ Ollama connected: {len(models)} models available")
            for model in models:
                print(f"    - {model['name']} ({model['details']['parameter_size']})")
            return True, f"Connected with {len(models)} models"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Connection failed: {e}"

async def test_gaming_advice():
    """Test gaming advice generation"""
    print("\n🎮 Testing Gaming Advice Generation...")
    
    try:
        from unified_gaming_ai_api import UnifiedGamingAI, create_request
        
        api = UnifiedGamingAI()
        
        # Test different gaming advice scenarios
        advice_tests = [
            {
                "name": "VALORANT FPS Optimization",
                "query": "How can I improve my FPS in VALORANT? I'm getting 60 FPS but want 144 FPS.",
                "context": {
                    "game": "VALORANT",
                    "current_fps": 60,
                    "target_fps": 144,
                    "resolution": "1920x1080",
                    "gpu": "RTX 3060"
                }
            },
            {
                "name": "CS:GO Aim Improvement",
                "query": "What are the best settings and practice routines to improve my aim in CS:GO?",
                "context": {
                    "game": "CS:GO",
                    "rank": "Gold Nova",
                    "sensitivity": 2.5,
                    "dpi": 800
                }
            },
            {
                "name": "Fortnite Building Tips",
                "query": "How can I improve my building speed and techniques in Fortnite competitive?",
                "context": {
                    "game": "Fortnite",
                    "mode": "competitive",
                    "current_skill": "intermediate",
                    "input": "keyboard_mouse"
                }
            }
        ]
        
        successful_tests = 0
        
        for i, test in enumerate(advice_tests, 1):
            print(f"\n  🎯 Test {i}: {test['name']}")
            
            request = create_request(
                "ai_assistance",
                "get_gaming_advice",
                {
                    "query": test["query"],
                    "context": test["context"]
                }
            )
            
            start_time = time.time()
            response = await api.process_request(request)
            response_time = time.time() - start_time
            
            if response.success:
                advice = response.data.get("ai_advice", "")
                print(f"    ✅ Success ({response_time:.2f}s)")
                print(f"    📝 Advice length: {len(advice)} characters")
                print(f"    🎯 Preview: {advice[:100]}...")
                successful_tests += 1
            else:
                print(f"    ❌ Failed: {response.error}")
        
        return successful_tests == len(advice_tests), f"Gaming advice: {successful_tests}/{len(advice_tests)} tests passed"
        
    except Exception as e:
        return False, f"Gaming advice test failed: {e}"

async def test_performance_analysis():
    """Test AI performance analysis"""
    print("\n📊 Testing AI Performance Analysis...")
    
    try:
        from unified_gaming_ai_api import UnifiedGamingAI, create_request
        
        api = UnifiedGamingAI()
        
        # Test performance analysis scenarios
        performance_scenarios = [
            {
                "name": "High CPU Usage",
                "data": {
                    "fps": 45,
                    "cpu_usage": 95,
                    "gpu_usage": 60,
                    "memory_usage": 70,
                    "temperature": 85,
                    "game": "VALORANT"
                }
            },
            {
                "name": "GPU Bottleneck",
                "data": {
                    "fps": 30,
                    "cpu_usage": 40,
                    "gpu_usage": 99,
                    "memory_usage": 80,
                    "temperature": 78,
                    "game": "CS:GO"
                }
            },
            {
                "name": "Memory Issues",
                "data": {
                    "fps": 25,
                    "cpu_usage": 60,
                    "gpu_usage": 70,
                    "memory_usage": 95,
                    "temperature": 70,
                    "game": "Fortnite"
                }
            }
        ]
        
        successful_analyses = 0
        
        for i, scenario in enumerate(performance_scenarios, 1):
            print(f"\n  📈 Analysis {i}: {scenario['name']}")
            
            request = create_request(
                "ai_assistance",
                "analyze_performance",
                {"performance_data": scenario["data"]}
            )
            
            start_time = time.time()
            response = await api.process_request(request)
            response_time = time.time() - start_time
            
            if response.success:
                analysis = response.data.get("ai_analysis", "")
                print(f"    ✅ Success ({response_time:.2f}s)")
                print(f"    📊 Analysis length: {len(analysis)} characters")
                print(f"    🔍 Preview: {analysis[:100]}...")
                successful_analyses += 1
            else:
                print(f"    ❌ Failed: {response.error}")
        
        return successful_analyses == len(performance_scenarios), f"Performance analysis: {successful_analyses}/{len(performance_scenarios)} tests passed"
        
    except Exception as e:
        return False, f"Performance analysis test failed: {e}"

async def test_optimization_suggestions():
    """Test AI optimization suggestions"""
    print("\n⚙️ Testing AI Optimization Suggestions...")
    
    try:
        from unified_gaming_ai_api import UnifiedGamingAI, create_request
        
        api = UnifiedGamingAI()
        
        # Test optimization suggestion scenarios
        optimization_scenarios = [
            {
                "name": "Competitive VALORANT Setup",
                "context": {
                    "game": "VALORANT",
                    "mode": "competitive",
                    "resolution": "1920x1080",
                    "target_fps": 240,
                    "hardware": "RTX 4070, i7-12700K, 32GB RAM"
                }
            },
            {
                "name": "CS:GO Pro Settings",
                "context": {
                    "game": "CS:GO",
                    "mode": "matchmaking",
                    "resolution": "1280x960",
                    "target_fps": 300,
                    "hardware": "RTX 3080, i5-11600K, 16GB RAM"
                }
            },
            {
                "name": "Fortnite Performance Mode",
                "context": {
                    "game": "Fortnite",
                    "mode": "arena",
                    "resolution": "1920x1080",
                    "target_fps": 165,
                    "hardware": "RTX 3060 Ti, Ryzen 5 5600X, 16GB RAM"
                }
            }
        ]
        
        successful_suggestions = 0
        
        for i, scenario in enumerate(optimization_scenarios, 1):
            print(f"\n  ⚙️ Suggestion {i}: {scenario['name']}")
            
            request = create_request(
                "ai_assistance",
                "suggest_optimizations",
                {"game_context": scenario["context"]}
            )
            
            start_time = time.time()
            response = await api.process_request(request)
            response_time = time.time() - start_time
            
            if response.success:
                suggestions = response.data.get("ai_suggestions", "")
                print(f"    ✅ Success ({response_time:.2f}s)")
                print(f"    💡 Suggestions length: {len(suggestions)} characters")
                print(f"    🎯 Preview: {suggestions[:100]}...")
                successful_suggestions += 1
            else:
                print(f"    ❌ Failed: {response.error}")
        
        return successful_suggestions == len(optimization_scenarios), f"Optimization suggestions: {successful_suggestions}/{len(optimization_scenarios)} tests passed"
        
    except Exception as e:
        return False, f"Optimization suggestions test failed: {e}"

async def test_ai_insights():
    """Test AI insights generation"""
    print("\n🧠 Testing AI Insights Generation...")
    
    try:
        from unified_gaming_ai_api import UnifiedGamingAI, create_request
        
        api = UnifiedGamingAI()
        
        # Test AI insights with different operations
        insight_tests = [
            {
                "name": "Game Optimization Insights",
                "feature": "game_optimization",
                "action": "apply_optimizations",
                "parameters": {"game_type": "valorant"}
            },
            {
                "name": "Performance Monitoring Insights",
                "feature": "performance_monitoring",
                "action": "get_current_performance",
                "parameters": {}
            },
            {
                "name": "Team Behavior Insights",
                "feature": "team_behaviors",
                "action": "execute_behavior",
                "parameters": {"behavior_type": "coordinated_attack"}
            }
        ]
        
        successful_insights = 0
        
        for i, test in enumerate(insight_tests, 1):
            print(f"\n  🧠 Insight {i}: {test['name']}")
            
            # Create request with AI assistance enabled
            request = create_request(
                test["feature"],
                test["action"],
                test["parameters"],
                ai_assistance=True
            )
            
            start_time = time.time()
            response = await api.process_request(request)
            response_time = time.time() - start_time
            
            if response.success and response.ai_insights:
                insights = response.ai_insights.get("insights", "")
                print(f"    ✅ Success ({response_time:.2f}s)")
                print(f"    🧠 Insights length: {len(insights)} characters")
                print(f"    💭 Preview: {insights[:100]}...")
                successful_insights += 1
            else:
                print(f"    ❌ Failed: {response.error or 'No insights generated'}")
        
        return successful_insights == len(insight_tests), f"AI insights: {successful_insights}/{len(insight_tests)} tests passed"
        
    except Exception as e:
        return False, f"AI insights test failed: {e}"

async def test_comprehensive_ai_workflow():
    """Test comprehensive AI-enhanced gaming workflow"""
    print("\n🎮 Testing Comprehensive AI-Enhanced Workflow...")
    
    try:
        from unified_gaming_ai_api import UnifiedGamingAI, create_request
        
        api = UnifiedGamingAI()
        
        print("  🎯 Scenario: Optimizing VALORANT competitive setup with AI assistance")
        
        workflow_steps = []
        
        # Step 1: Get gaming advice
        print("\n    1. Getting AI gaming advice...")
        advice_request = create_request(
            "ai_assistance",
            "get_gaming_advice",
            {
                "query": "I want to optimize my VALORANT setup for competitive play. What should I focus on?",
                "context": {"game": "VALORANT", "mode": "competitive", "rank": "Diamond"}
            }
        )
        advice_response = await api.process_request(advice_request)
        workflow_steps.append(advice_response.success)
        print(f"       {'✅' if advice_response.success else '❌'} Gaming advice: {len(advice_response.data.get('ai_advice', '')) if advice_response.success else 'Failed'} chars")
        
        # Step 2: Apply optimizations with AI insights
        print("\n    2. Applying game optimizations with AI insights...")
        opt_request = create_request(
            "game_optimization",
            "apply_optimizations",
            {"game_type": "valorant"},
            ai_assistance=True
        )
        opt_response = await api.process_request(opt_request)
        workflow_steps.append(opt_response.success)
        print(f"       {'✅' if opt_response.success else '❌'} Optimizations: {opt_response.data.get('optimizations_applied', 0) if opt_response.success else 'Failed'} applied")
        if opt_response.ai_insights:
            print(f"       🧠 AI insights: {len(opt_response.ai_insights.get('insights', ''))} chars")
        
        # Step 3: Start performance monitoring
        print("\n    3. Starting performance monitoring...")
        perf_start_request = create_request("performance_monitoring", "start_monitoring")
        perf_start_response = await api.process_request(perf_start_request)
        workflow_steps.append(perf_start_response.success)
        print(f"       {'✅' if perf_start_response.success else '❌'} Monitoring: {'Started' if perf_start_response.success else 'Failed'}")
        
        # Wait for performance data
        await asyncio.sleep(1.0)
        
        # Step 4: Get performance analysis with AI
        print("\n    4. Getting AI performance analysis...")
        perf_request = create_request(
            "performance_monitoring",
            "get_current_performance",
            ai_assistance=True
        )
        perf_response = await api.process_request(perf_request)
        workflow_steps.append(perf_response.success)
        print(f"       {'✅' if perf_response.success else '❌'} Performance data: {'Available' if perf_response.success else 'Failed'}")
        if perf_response.ai_insights:
            print(f"       🧠 AI insights: {len(perf_response.ai_insights.get('insights', ''))} chars")
        
        # Step 5: Get optimization suggestions
        print("\n    5. Getting AI optimization suggestions...")
        suggest_request = create_request(
            "ai_assistance",
            "suggest_optimizations",
            {
                "game_context": {
                    "game": "VALORANT",
                    "mode": "competitive",
                    "current_fps": 144,
                    "target_fps": 240
                }
            }
        )
        suggest_response = await api.process_request(suggest_request)
        workflow_steps.append(suggest_response.success)
        print(f"       {'✅' if suggest_response.success else '❌'} Suggestions: {len(suggest_response.data.get('ai_suggestions', '')) if suggest_response.success else 'Failed'} chars")
        
        # Step 6: Stop monitoring
        print("\n    6. Stopping performance monitoring...")
        perf_stop_request = create_request("performance_monitoring", "stop_monitoring")
        perf_stop_response = await api.process_request(perf_stop_request)
        workflow_steps.append(perf_stop_response.success)
        print(f"       {'✅' if perf_stop_response.success else '❌'} Monitoring: {'Stopped' if perf_stop_response.success else 'Failed'}")
        
        successful_steps = sum(workflow_steps)
        total_steps = len(workflow_steps)
        
        print(f"\n  📊 Workflow Results: {successful_steps}/{total_steps} steps successful")
        
        return successful_steps >= 5, f"AI workflow: {successful_steps}/{total_steps} steps successful"
        
    except Exception as e:
        return False, f"AI workflow test failed: {e}"

async def main():
    """Main Ollama live test execution"""
    print("🤖 OLLAMA LIVE TEST - GAMING AI")
    print("=" * 60)
    print("Testing Gaming AI with real Ollama LLM integration")
    print("=" * 60)
    
    setup_logging()
    
    test_results = {}
    
    # Test 1: Ollama Connection
    print("\n" + "="*60)
    connection_success, connection_result = await test_ollama_connection()
    test_results['ollama_connection'] = {'success': connection_success, 'result': connection_result}
    
    if not connection_success:
        print("❌ Ollama not available. Please start Ollama service.")
        return False
    
    # Test 2: Gaming Advice
    print("\n" + "="*60)
    advice_success, advice_result = await test_gaming_advice()
    test_results['gaming_advice'] = {'success': advice_success, 'result': advice_result}
    
    # Test 3: Performance Analysis
    print("\n" + "="*60)
    analysis_success, analysis_result = await test_performance_analysis()
    test_results['performance_analysis'] = {'success': analysis_success, 'result': analysis_result}
    
    # Test 4: Optimization Suggestions
    print("\n" + "="*60)
    suggestions_success, suggestions_result = await test_optimization_suggestions()
    test_results['optimization_suggestions'] = {'success': suggestions_success, 'result': suggestions_result}
    
    # Test 5: AI Insights
    print("\n" + "="*60)
    insights_success, insights_result = await test_ai_insights()
    test_results['ai_insights'] = {'success': insights_success, 'result': insights_result}
    
    # Test 6: Comprehensive Workflow
    print("\n" + "="*60)
    workflow_success, workflow_result = await test_comprehensive_ai_workflow()
    test_results['ai_workflow'] = {'success': workflow_success, 'result': workflow_result}
    
    # Final Results
    print("\n" + "="*60)
    print("🎊 OLLAMA LIVE TEST RESULTS")
    print("=" * 60)
    
    # Calculate success metrics
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result['success'])
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    for test_name, result in test_results.items():
        status = '✅ PASS' if result['success'] else '❌ FAIL'
        print(f"🤖 {test_name.replace('_', ' ').title()}: {status}")
        print(f"    📝 {result['result']}")
    
    # Overall Assessment
    print("\n" + "="*60)
    if success_rate >= 90:
        print("🎉 EXCELLENT: Ollama integration is working perfectly!")
        print("✅ Gaming AI + Ollama ready for production use")
    elif success_rate >= 75:
        print("✅ GOOD: Ollama integration is mostly working")
        print("⚠️ Minor issues that can be addressed")
    elif success_rate >= 50:
        print("⚠️ MODERATE: Ollama integration has significant issues")
        print("🔧 Needs attention before production use")
    else:
        print("❌ CRITICAL: Ollama integration is not working properly")
        print("🚨 Major fixes required")
    
    print("=" * 60)
    return success_rate >= 75

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
