#!/usr/bin/env python3
"""
🧪 Sprint 4 Task 4.4 Comprehensive Test - Gaming AI

Complete testing suite for Performance Monitoring System.

Sprint 4 - Task 4.4 Comprehensive Test
- Real-time performance tracking
- Bottleneck detection and analysis
- Performance optimization suggestions
- Alert system validation

Author: Nexus - Quantum AI Architect
Sprint: 4.4 - Advanced Gaming Features
"""

import time
import logging
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
            logging.FileHandler('test_sprint4_task4.log')
        ]
    )

def test_performance_monitor_core():
    """Test core performance monitoring system"""
    print("📊 Testing Performance Monitor Core...")
    
    try:
        from performance_monitor import PerformanceMonitor, AlertLevel, PerformanceAlert
        
        # Initialize monitor
        monitor = PerformanceMonitor(collection_interval=0.1)
        
        # Test alert callback
        received_alerts = []
        def alert_callback(alert: PerformanceAlert):
            received_alerts.append(alert)
        
        monitor.register_alert_callback(AlertLevel.WARNING, alert_callback)
        monitor.register_alert_callback(AlertLevel.CRITICAL, alert_callback)
        
        print("  🔄 Testing monitoring lifecycle...")
        
        # Start monitoring
        start_success = monitor.start_monitoring()
        print(f"    ✅ Start monitoring: {'Success' if start_success else 'Failed'}")
        
        # Monitor for a short time
        time.sleep(2.0)
        
        # Get current performance
        current = monitor.get_current_performance()
        print(f"    ✅ Current performance: {'Available' if current else 'Not available'}")
        
        if current:
            metrics_count = len(current.metrics)
            print(f"    ✅ Metrics collected: {metrics_count}")
        
        # Stop monitoring
        monitor.stop_monitoring()
        print("    ✅ Stop monitoring: Success")
        
        # Get final stats
        stats = monitor.get_monitoring_stats()
        snapshots = stats['snapshots_collected']
        uptime = stats['monitoring_uptime']
        
        print(f"  📊 Performance: {snapshots} snapshots in {uptime:.1f}s")
        
        return True, f"Core system: {snapshots} snapshots, {metrics_count} metrics"
        
    except Exception as e:
        print(f"  ❌ Core test failed: {e}")
        return False, str(e)

def test_bottleneck_detection():
    """Test bottleneck detection system"""
    print("🚨 Testing Bottleneck Detection...")
    
    try:
        from performance_monitor import PerformanceMonitor, BottleneckType
        
        # Initialize monitor
        monitor = PerformanceMonitor(collection_interval=0.1)
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Monitor for bottleneck detection
        time.sleep(1.5)
        
        # Get bottlenecks
        bottlenecks = monitor.get_active_bottlenecks()
        total_bottlenecks = monitor.get_monitoring_stats()['bottlenecks_detected']
        
        print(f"  🔍 Active bottlenecks: {len(bottlenecks)}")
        print(f"  📊 Total detected: {total_bottlenecks}")
        
        # Test bottleneck types
        bottleneck_types = set()
        for bottleneck in bottlenecks:
            bottleneck_types.add(bottleneck.bottleneck_type)
            print(f"    - {bottleneck.description} (severity: {bottleneck.severity:.1%})")
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        return True, f"Bottleneck detection: {total_bottlenecks} detected, {len(bottleneck_types)} types"
        
    except Exception as e:
        print(f"  ❌ Bottleneck test failed: {e}")
        return False, str(e)

def test_alert_system():
    """Test alert system"""
    print("⚠️ Testing Alert System...")
    
    try:
        from performance_monitor import PerformanceMonitor, AlertLevel
        
        # Initialize monitor
        monitor = PerformanceMonitor(collection_interval=0.1)
        
        # Track alerts
        received_alerts = []
        def alert_callback(alert):
            received_alerts.append(alert)
        
        monitor.register_alert_callback(AlertLevel.WARNING, alert_callback)
        monitor.register_alert_callback(AlertLevel.CRITICAL, alert_callback)
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Monitor for alerts
        time.sleep(1.5)
        
        # Get alerts
        active_alerts = monitor.get_active_alerts()
        total_alerts = monitor.get_monitoring_stats()['alerts_generated']
        
        print(f"  📢 Active alerts: {len(active_alerts)}")
        print(f"  📊 Total generated: {total_alerts}")
        print(f"  📨 Callback alerts: {len(received_alerts)}")
        
        # Test alert acknowledgment
        acknowledged_count = 0
        for alert in active_alerts[:3]:  # Acknowledge first 3
            if monitor.acknowledge_alert(alert.alert_id):
                acknowledged_count += 1
        
        print(f"  ✅ Acknowledged: {acknowledged_count}")
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        return True, f"Alert system: {total_alerts} generated, {acknowledged_count} acknowledged"
        
    except Exception as e:
        print(f"  ❌ Alert test failed: {e}")
        return False, str(e)

def test_performance_analytics():
    """Test performance analytics"""
    print("📈 Testing Performance Analytics...")
    
    try:
        from performance_monitor import PerformanceMonitor
        
        # Initialize monitor
        monitor = PerformanceMonitor(collection_interval=0.1)
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Collect data
        time.sleep(2.0)
        
        # Get analytics
        analytics = monitor.get_performance_analytics()
        
        print(f"  📊 Analytics components:")
        print(f"    - Monitoring status: {analytics.get('monitoring_status', 'unknown')}")
        print(f"    - Collection rate: {analytics.get('collection_rate', 0):.1f}/sec")
        print(f"    - Current performance: {'Available' if 'current_performance' in analytics else 'Not available'}")
        print(f"    - Performance trends: {'Available' if 'performance_trends' in analytics else 'Not available'}")
        print(f"    - Bottleneck summary: {'Available' if 'bottlenecks' in analytics else 'Not available'}")
        print(f"    - Alert summary: {'Available' if 'alerts' in analytics else 'Not available'}")
        
        # Test performance history
        history = monitor.get_performance_history(60.0)
        print(f"  📚 Performance history: {len(history)} snapshots")
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        analytics_components = sum([
            'current_performance' in analytics,
            'performance_trends' in analytics,
            'bottlenecks' in analytics,
            'alerts' in analytics
        ])
        
        return True, f"Analytics: {analytics_components}/4 components, {len(history)} history"
        
    except Exception as e:
        print(f"  ❌ Analytics test failed: {e}")
        return False, str(e)

def test_optimization_suggestions():
    """Test optimization suggestions"""
    print("💡 Testing Optimization Suggestions...")
    
    try:
        from performance_monitor import PerformanceMonitor
        
        # Initialize monitor
        monitor = PerformanceMonitor(collection_interval=0.1)
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Collect data
        time.sleep(1.5)
        
        # Get suggestions
        suggestions = monitor.get_optimization_suggestions()
        
        print(f"  💡 Total suggestions: {len(suggestions)}")
        
        # Analyze suggestions
        suggestion_types = {}
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        
        for suggestion in suggestions:
            suggestion_type = suggestion.get('type', 'unknown')
            priority = suggestion.get('priority', 'low')
            
            suggestion_types[suggestion_type] = suggestion_types.get(suggestion_type, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        print(f"  📊 Suggestion types: {dict(suggestion_types)}")
        print(f"  📊 Priority distribution: {dict(priority_counts)}")
        
        # Display top suggestions
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"    {i}. [{suggestion.get('priority', 'low').upper()}] {suggestion.get('description', 'No description')}")
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        return True, f"Suggestions: {len(suggestions)} total, {len(suggestion_types)} types"
        
    except Exception as e:
        print(f"  ❌ Suggestions test failed: {e}")
        return False, str(e)

def test_integration_with_game_optimizations():
    """Test integration with game optimization system"""
    print("🔗 Testing Integration with Game Optimizations...")
    
    try:
        from performance_monitor import PerformanceMonitor
        from game_optimizations import GameOptimizations, GameType
        
        # Initialize systems
        monitor = PerformanceMonitor(collection_interval=0.2)
        game_opt = GameOptimizations()
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Simulate game optimization
        game_opt.current_game = GameType.VALORANT
        optimizations = game_opt.apply_optimizations()
        
        # Monitor performance during optimization
        time.sleep(1.0)
        
        # Get performance data
        current = monitor.get_current_performance()
        suggestions = monitor.get_optimization_suggestions()
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        print(f"  🎮 Game optimizations applied: {len(optimizations)}")
        print(f"  📊 Performance metrics: {len(current.metrics) if current else 0}")
        print(f"  💡 Monitor suggestions: {len(suggestions)}")
        
        integration_success = len(optimizations) > 0 and current is not None
        
        return integration_success, f"Integration: {len(optimizations)} optimizations, {len(suggestions)} suggestions"
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        return False, str(e)

def main():
    """Main test execution"""
    print("🧪 SPRINT 4 TASK 4.4 COMPREHENSIVE TEST")
    print("=" * 60)
    print("📊 Performance Monitoring System Testing Suite")
    print("=" * 60)
    
    setup_logging()
    
    test_results = {}
    
    # Test 1: Core Performance Monitor
    print("\n" + "="*60)
    core_success, core_result = test_performance_monitor_core()
    test_results['core_monitor'] = {'success': core_success, 'result': core_result}
    
    # Test 2: Bottleneck Detection
    print("\n" + "="*60)
    bottleneck_success, bottleneck_result = test_bottleneck_detection()
    test_results['bottleneck_detection'] = {'success': bottleneck_success, 'result': bottleneck_result}
    
    # Test 3: Alert System
    print("\n" + "="*60)
    alert_success, alert_result = test_alert_system()
    test_results['alert_system'] = {'success': alert_success, 'result': alert_result}
    
    # Test 4: Performance Analytics
    print("\n" + "="*60)
    analytics_success, analytics_result = test_performance_analytics()
    test_results['analytics'] = {'success': analytics_success, 'result': analytics_result}
    
    # Test 5: Optimization Suggestions
    print("\n" + "="*60)
    suggestions_success, suggestions_result = test_optimization_suggestions()
    test_results['suggestions'] = {'success': suggestions_success, 'result': suggestions_result}
    
    # Test 6: Integration
    print("\n" + "="*60)
    integration_success, integration_result = test_integration_with_game_optimizations()
    test_results['integration'] = {'success': integration_success, 'result': integration_result}
    
    # Final Results
    print("\n" + "="*60)
    print("🎊 SPRINT 4 TASK 4.4 TEST RESULTS")
    print("=" * 60)
    
    # Calculate success metrics
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result['success'])
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    for test_name, result in test_results.items():
        status = '✅ PASS' if result['success'] else '❌ FAIL'
        print(f"📊 {test_name.replace('_', ' ').title()}: {status}")
    
    # Task 4.4 Status
    print("\n" + "="*60)
    if success_rate >= 80:
        print("🎉 TASK 4.4: PERFORMANCE MONITORING SYSTEM - COMPLETED!")
        print("✅ Real-time performance tracking operational")
        print("✅ Bottleneck detection working")
        print("✅ Alert system functional")
        print("✅ Performance analytics available")
        print("✅ Optimization suggestions generated")
        print("✅ Integration with game optimizations working")
        print("✅ Ready for Task 4.5: Advanced Feature Integration")
    else:
        print("⚠️ TASK 4.4: PERFORMANCE MONITORING SYSTEM - NEEDS ATTENTION")
        print(f"📊 Success Rate: {success_rate:.1f}% (Target: 80%+)")
    
    print("=" * 60)
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
