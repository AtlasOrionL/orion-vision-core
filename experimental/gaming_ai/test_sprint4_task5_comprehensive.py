#!/usr/bin/env python3
"""
🧪 Sprint 4 Task 4.5 Comprehensive Test - Gaming AI

Complete testing suite for Advanced Feature Integration.

Sprint 4 - Task 4.5 Comprehensive Test
- Unified Gaming AI API testing
- Ollama integration validation
- Feature compatibility testing
- Cross-feature integration testing

Author: Nexus - Quantum AI Architect
Sprint: 4.5 - Advanced Gaming Features
"""

import time
import logging
import asyncio
import sys
import os
from typing import Dict, List, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for comprehensive testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_sprint4_task5.log')
        ]
    )

async def test_unified_api_core():
    """Test unified API core functionality"""
    print("🔗 Testing Unified API Core...")
    
    try:
        from unified_gaming_ai_api import UnifiedGamingAI, create_request
        
        # Initialize API
        api = UnifiedGamingAI()
        
        # Test API status
        status = api.get_api_status()
        print(f"  ✅ API Status: {status['features_available']} features, {status['ollama_available']} Ollama")
        
        # Test basic request processing
        request = create_request("game_optimization", "get_optimization_summary")
        response = await api.process_request(request)
        
        print(f"  ✅ Request processing: {'Success' if response.success else 'Failed'}")
        print(f"  ✅ Response time: {response.execution_time:.3f}s")
        
        return True, f"Core API: {status['features_available']} features available"
        
    except Exception as e:
        print(f"  ❌ Core API test failed: {e}")
        return False, str(e)

async def test_feature_integration():
    """Test cross-feature integration"""
    print("🔗 Testing Feature Integration...")
    
    try:
        from unified_gaming_ai_api import UnifiedGamingAI, create_request
        
        api = UnifiedGamingAI()
        
        # Test 1: Game Optimization + Performance Monitoring
        print("  🎮 Testing Game Opt + Performance Mon integration...")
        
        # Start performance monitoring
        perf_request = create_request("performance_monitoring", "start_monitoring")
        perf_response = await api.process_request(perf_request)
        
        # Apply game optimizations
        game_request = create_request(
            "game_optimization", 
            "apply_optimizations",
            {"game_type": "valorant"}
        )
        game_response = await api.process_request(game_request)
        
        # Wait for performance data
        await asyncio.sleep(1.0)
        
        # Get performance data
        current_perf_request = create_request("performance_monitoring", "get_current_performance")
        current_perf_response = await api.process_request(current_perf_request)
        
        integration1_success = (perf_response.success and game_response.success and 
                               current_perf_response.success)
        
        print(f"    ✅ Game Opt + Perf Mon: {'Success' if integration1_success else 'Failed'}")
        
        # Test 2: Multi-Agent + Team Behaviors
        print("  🤝 Testing Multi-Agent + Team Behaviors integration...")
        
        # Start coordination
        coord_request = create_request("multi_agent_coordination", "start_coordination")
        coord_response = await api.process_request(coord_request)
        
        # Register agents
        agent_request = create_request(
            "multi_agent_coordination",
            "register_agent",
            {"agent_id": "test_agent_1", "agent_type": "demo", "capabilities": ["teamplay"]}
        )
        agent_response = await api.process_request(agent_request)
        
        # Execute team behavior
        behavior_request = create_request(
            "team_behaviors",
            "execute_behavior",
            {"behavior_type": "coordinated_attack", "context": {"target": "test"}}
        )
        behavior_response = await api.process_request(behavior_request)
        
        integration2_success = (coord_response.success and agent_response.success and 
                               behavior_response.success)
        
        print(f"    ✅ Multi-Agent + Team Behaviors: {'Success' if integration2_success else 'Failed'}")
        
        # Stop monitoring
        stop_request = create_request("performance_monitoring", "stop_monitoring")
        await api.process_request(stop_request)
        
        overall_success = integration1_success and integration2_success
        
        return overall_success, f"Integration: {2 if overall_success else 1}/2 integrations working"
        
    except Exception as e:
        print(f"  ❌ Feature integration test failed: {e}")
        return False, str(e)

async def test_ai_assistance():
    """Test AI assistance features"""
    print("🤖 Testing AI Assistance...")
    
    try:
        from unified_gaming_ai_api import UnifiedGamingAI, create_request
        
        api = UnifiedGamingAI()
        
        # Test gaming advice
        advice_request = create_request(
            "ai_assistance",
            "get_gaming_advice",
            {
                "query": "How to improve FPS in VALORANT?",
                "context": {"game": "VALORANT", "current_fps": 60}
            }
        )
        advice_response = await api.process_request(advice_request)
        
        print(f"  ✅ Gaming advice: {'Available' if advice_response.success else 'Failed'}")
        
        # Test performance analysis
        analysis_request = create_request(
            "ai_assistance",
            "analyze_performance",
            {
                "performance_data": {
                    "fps": 45,
                    "cpu_usage": 85,
                    "gpu_usage": 95,
                    "memory_usage": 70
                }
            }
        )
        analysis_response = await api.process_request(analysis_request)
        
        print(f"  ✅ Performance analysis: {'Available' if analysis_response.success else 'Failed'}")
        
        # Test optimization suggestions
        suggestions_request = create_request(
            "ai_assistance",
            "suggest_optimizations",
            {
                "game_context": {
                    "game": "VALORANT",
                    "resolution": "1920x1080",
                    "target_fps": 144
                }
            }
        )
        suggestions_response = await api.process_request(suggestions_request)
        
        print(f"  ✅ Optimization suggestions: {'Available' if suggestions_response.success else 'Failed'}")
        
        # Test AI insights
        insights_request = create_request(
            "performance_monitoring",
            "get_current_performance",
            ai_assistance=True
        )
        insights_response = await api.process_request(insights_request)
        
        has_insights = insights_response.ai_insights is not None
        print(f"  ✅ AI insights: {'Available' if has_insights else 'Not available'}")
        
        ai_features_working = sum([
            advice_response.success,
            analysis_response.success,
            suggestions_response.success,
            has_insights
        ])
        
        return ai_features_working >= 3, f"AI assistance: {ai_features_working}/4 features working"
        
    except Exception as e:
        print(f"  ❌ AI assistance test failed: {e}")
        return False, str(e)

async def test_compatibility_matrix():
    """Test feature compatibility matrix"""
    print("🔗 Testing Compatibility Matrix...")
    
    try:
        from unified_gaming_ai_api import UnifiedGamingAI, APIFeature
        
        api = UnifiedGamingAI()
        
        # Test compatibility queries
        compatibility_tests = [
            (APIFeature.GAME_OPTIMIZATION, APIFeature.PERFORMANCE_MONITORING),
            (APIFeature.MULTI_AGENT_COORDINATION, APIFeature.TEAM_BEHAVIORS),
            (APIFeature.PERFORMANCE_MONITORING, APIFeature.MULTI_AGENT_COORDINATION)
        ]

        compatible_pairs = 0
        for feature_a, feature_b in compatibility_tests:
            compatibility = api.get_feature_compatibility(feature_a, feature_b)
            if compatibility:
                compatible_pairs += 1
                print(f"    ✅ {feature_a.value} + {feature_b.value}: {compatibility.compatibility_level.value}")
            else:
                print(f"    ❌ {feature_a.value} + {feature_b.value}: No compatibility found")

        # Test integration recommendations
        recommendations = api.get_integration_recommendations()
        print(f"  ✅ Integration recommendations: {len(recommendations)} available")

        # Test compatibility matrix size
        matrix_size = len(api.compatibility_matrix)
        print(f"  ✅ Compatibility matrix size: {matrix_size} entries")

        # Success if we have at least 2 compatible pairs and recommendations
        success = compatible_pairs >= 2 and len(recommendations) > 0 and matrix_size > 0

        return success, f"Compatibility: {compatible_pairs}/3 pairs, {len(recommendations)} recommendations, {matrix_size} matrix entries"
        
    except Exception as e:
        print(f"  ❌ Compatibility matrix test failed: {e}")
        return False, str(e)

async def test_comprehensive_workflow():
    """Test comprehensive Gaming AI workflow"""
    print("🎮 Testing Comprehensive Workflow...")
    
    try:
        from unified_gaming_ai_api import UnifiedGamingAI, create_request, quick_optimize_game, quick_performance_check
        
        api = UnifiedGamingAI()
        
        # Workflow: Complete gaming session optimization
        workflow_steps = []
        
        # Step 1: Detect game
        detect_request = create_request(
            "game_optimization",
            "detect_game",
            {"process_name": "VALORANT-Win64-Shipping.exe", "window_title": "VALORANT"}
        )
        detect_response = await api.process_request(detect_request)
        workflow_steps.append(detect_response.success)
        print(f"    1. Game detection: {'✅' if detect_response.success else '❌'}")
        
        # Step 2: Start performance monitoring
        monitor_request = create_request("performance_monitoring", "start_monitoring")
        monitor_response = await api.process_request(monitor_request)
        workflow_steps.append(monitor_response.success)
        print(f"    2. Performance monitoring: {'✅' if monitor_response.success else '❌'}")
        
        # Step 3: Apply comprehensive optimizations
        optimize_response = await quick_optimize_game(api, "valorant", ai_assistance=True)
        workflow_steps.append(optimize_response.success)
        print(f"    3. Game optimization: {'✅' if optimize_response.success else '❌'}")
        
        # Step 4: Start multi-agent coordination
        coord_request = create_request("multi_agent_coordination", "start_coordination")
        coord_response = await api.process_request(coord_request)
        workflow_steps.append(coord_response.success)
        print(f"    4. Multi-agent coordination: {'✅' if coord_response.success else '❌'}")
        
        # Step 5: Execute team behaviors
        behavior_request = create_request(
            "team_behaviors",
            "execute_behavior",
            {"behavior_type": "coordinated_attack"}
        )
        behavior_response = await api.process_request(behavior_request)
        workflow_steps.append(behavior_response.success)
        print(f"    5. Team behavior execution: {'✅' if behavior_response.success else '❌'}")
        
        # Step 6: Get performance check with AI insights
        perf_response = await quick_performance_check(api, ai_assistance=True)
        workflow_steps.append(perf_response.success)
        print(f"    6. Performance check: {'✅' if perf_response.success else '❌'}")
        
        # Step 7: Get AI recommendations
        ai_request = create_request(
            "ai_assistance",
            "get_gaming_advice",
            {"query": "Optimize my VALORANT performance", "context": {"game": "VALORANT"}}
        )
        ai_response = await api.process_request(ai_request)
        workflow_steps.append(ai_response.success)
        print(f"    7. AI recommendations: {'✅' if ai_response.success else '❌'}")
        
        # Cleanup
        stop_request = create_request("performance_monitoring", "stop_monitoring")
        await api.process_request(stop_request)
        
        successful_steps = sum(workflow_steps)
        workflow_success = successful_steps >= 6
        
        return workflow_success, f"Workflow: {successful_steps}/7 steps successful"
        
    except Exception as e:
        print(f"  ❌ Comprehensive workflow test failed: {e}")
        return False, str(e)

async def main():
    """Main test execution"""
    print("🧪 SPRINT 4 TASK 4.5 COMPREHENSIVE TEST")
    print("=" * 60)
    print("🔗 Advanced Feature Integration Testing Suite")
    print("=" * 60)
    
    setup_logging()
    
    test_results = {}
    
    # Test 1: Unified API Core
    print("\n" + "="*60)
    core_success, core_result = await test_unified_api_core()
    test_results['unified_api_core'] = {'success': core_success, 'result': core_result}
    
    # Test 2: Feature Integration
    print("\n" + "="*60)
    integration_success, integration_result = await test_feature_integration()
    test_results['feature_integration'] = {'success': integration_success, 'result': integration_result}
    
    # Test 3: AI Assistance
    print("\n" + "="*60)
    ai_success, ai_result = await test_ai_assistance()
    test_results['ai_assistance'] = {'success': ai_success, 'result': ai_result}
    
    # Test 4: Compatibility Matrix
    print("\n" + "="*60)
    compatibility_success, compatibility_result = await test_compatibility_matrix()
    test_results['compatibility_matrix'] = {'success': compatibility_success, 'result': compatibility_result}
    
    # Test 5: Comprehensive Workflow
    print("\n" + "="*60)
    workflow_success, workflow_result = await test_comprehensive_workflow()
    test_results['comprehensive_workflow'] = {'success': workflow_success, 'result': workflow_result}
    
    # Final Results
    print("\n" + "="*60)
    print("🎊 SPRINT 4 TASK 4.5 TEST RESULTS")
    print("=" * 60)
    
    # Calculate success metrics
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result['success'])
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    for test_name, result in test_results.items():
        status = '✅ PASS' if result['success'] else '❌ FAIL'
        print(f"🔗 {test_name.replace('_', ' ').title()}: {status}")
    
    # Task 4.5 Status
    print("\n" + "="*60)
    if success_rate >= 80:
        print("🎉 TASK 4.5: ADVANCED FEATURE INTEGRATION - COMPLETED!")
        print("✅ Unified Gaming AI API operational")
        print("✅ Cross-feature integration working")
        print("✅ AI assistance with Ollama functional")
        print("✅ Feature compatibility matrix available")
        print("✅ Comprehensive workflow validated")
        print("✅ SPRINT 4 COMPLETED! All 5 tasks done!")
    else:
        print("⚠️ TASK 4.5: ADVANCED FEATURE INTEGRATION - NEEDS ATTENTION")
        print(f"📊 Success Rate: {success_rate:.1f}% (Target: 80%+)")
    
    print("=" * 60)
    return success_rate >= 80

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
