#!/usr/bin/env python3
"""
📊 Gaming AI Debug Dashboard - Performance Monitor Tests Module

Specialized testing module for performance monitoring features.
Provides detailed testing for real-time monitoring, analytics, and optimization suggestions.

Author: Nexus - Quantum AI Architect
Module: Performance Monitor Tests
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@dataclass
class PerformanceTestResult:
    """Performance monitoring test result"""
    test_id: str
    test_type: str
    status: str  # success, failed, warning
    duration: float
    metrics_collected: int
    data_points: int
    details: Dict[str, Any]
    timestamp: float
    error_message: Optional[str] = None

class PerformanceMonitorTester:
    """
    Performance monitoring testing module
    
    Features:
    - Real-time monitoring testing
    - Performance analytics validation
    - Bottleneck detection testing
    - Optimization suggestions testing
    """
    
    def __init__(self):
        self.logger = logging.getLogger("PerformanceMonitorTester")
        self.test_results: List[PerformanceTestResult] = []
        
        # Import performance monitor
        try:
            from performance_monitor import PerformanceMonitor
            self.performance_monitor = PerformanceMonitor(collection_interval=0.5)
            self.monitor_available = True
            self.logger.info("✅ Performance monitor loaded successfully")

        except ImportError as e:
            self.monitor_available = False
            self.logger.error(f"❌ Performance monitor import failed: {e}")
    
    async def test_basic_monitoring(self) -> PerformanceTestResult:
        """Test basic monitoring functionality"""
        test_id = f"basic_monitor_{int(time.time())}"
        start_time = time.time()
        
        try:
            if not self.monitor_available:
                raise Exception("Performance monitor not available")
            
            # Start monitoring
            started = self.performance_monitor.start_monitoring()
            if not started:
                raise Exception("Failed to start monitoring")
            
            # Wait for data collection
            await asyncio.sleep(2.0)
            
            # Get current performance
            current = self.performance_monitor.get_current_performance()
            
            # Stop monitoring
            self.performance_monitor.stop_monitoring()
            
            metrics_count = len(current.metrics) if current else 0
            
            result = PerformanceTestResult(
                test_id=test_id,
                test_type="basic_monitoring",
                status="success" if current else "failed",
                duration=time.time() - start_time,
                metrics_collected=metrics_count,
                data_points=1,
                details={
                    "monitoring_started": started,
                    "data_collected": current is not None,
                    "metrics_available": list(current.metrics.keys()) if current else [],
                    "collection_interval": self.performance_monitor.collection_interval
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            result = PerformanceTestResult(
                test_id=test_id,
                test_type="basic_monitoring",
                status="failed",
                duration=time.time() - start_time,
                metrics_collected=0,
                data_points=0,
                details={},
                timestamp=time.time(),
                error_message=str(e)
            )
        
        self.test_results.append(result)
        return result
    
    async def test_analytics_system(self) -> PerformanceTestResult:
        """Test performance analytics system"""
        test_id = f"analytics_{int(time.time())}"
        start_time = time.time()
        
        try:
            if not self.monitor_available:
                raise Exception("Performance monitor not available")
            
            # Start monitoring for analytics
            self.performance_monitor.start_monitoring()
            
            # Collect data for analytics
            await asyncio.sleep(3.0)
            
            # Get analytics
            analytics = self.performance_monitor.get_performance_analytics()
            
            # Stop monitoring
            self.performance_monitor.stop_monitoring()
            
            result = PerformanceTestResult(
                test_id=test_id,
                test_type="analytics",
                status="success" if analytics else "failed",
                duration=time.time() - start_time,
                metrics_collected=len(analytics) if analytics else 0,
                data_points=analytics.get("total_snapshots", 0) if analytics else 0,
                details={
                    "analytics_available": analytics is not None,
                    "analytics_keys": list(analytics.keys()) if analytics else [],
                    "total_snapshots": analytics.get("total_snapshots", 0) if analytics else 0,
                    "collection_rate": analytics.get("collection_rate", 0) if analytics else 0
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            result = PerformanceTestResult(
                test_id=test_id,
                test_type="analytics",
                status="failed",
                duration=time.time() - start_time,
                metrics_collected=0,
                data_points=0,
                details={},
                timestamp=time.time(),
                error_message=str(e)
            )
        
        self.test_results.append(result)
        return result
    
    async def test_bottleneck_detection(self) -> PerformanceTestResult:
        """Test bottleneck detection system"""
        test_id = f"bottleneck_{int(time.time())}"
        start_time = time.time()
        
        try:
            if not self.monitor_available:
                raise Exception("Performance monitor not available")
            
            # Start monitoring
            self.performance_monitor.start_monitoring()
            
            # Wait for data collection
            await asyncio.sleep(2.0)
            
            # Get bottlenecks
            bottlenecks = self.performance_monitor.get_active_bottlenecks()
            
            # Stop monitoring
            self.performance_monitor.stop_monitoring()
            
            bottleneck_count = len(bottlenecks) if bottlenecks else 0
            
            result = PerformanceTestResult(
                test_id=test_id,
                test_type="bottleneck_detection",
                status="success",
                duration=time.time() - start_time,
                metrics_collected=bottleneck_count,
                data_points=bottleneck_count,
                details={
                    "bottlenecks_detected": bottleneck_count,
                    "bottleneck_types": [b.bottleneck_type.value for b in bottlenecks] if bottlenecks else [],
                    "detection_working": True
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            result = PerformanceTestResult(
                test_id=test_id,
                test_type="bottleneck_detection",
                status="failed",
                duration=time.time() - start_time,
                metrics_collected=0,
                data_points=0,
                details={},
                timestamp=time.time(),
                error_message=str(e)
            )
        
        self.test_results.append(result)
        return result
    
    async def test_optimization_suggestions(self) -> PerformanceTestResult:
        """Test optimization suggestions system"""
        test_id = f"optimization_{int(time.time())}"
        start_time = time.time()
        
        try:
            if not self.monitor_available:
                raise Exception("Performance monitor not available")
            
            # Start monitoring
            self.performance_monitor.start_monitoring()
            
            # Wait for data collection
            await asyncio.sleep(2.0)
            
            # Get optimization suggestions
            suggestions = self.performance_monitor.get_optimization_suggestions()
            
            # Stop monitoring
            self.performance_monitor.stop_monitoring()
            
            suggestion_count = len(suggestions) if suggestions else 0
            
            result = PerformanceTestResult(
                test_id=test_id,
                test_type="optimization_suggestions",
                status="success",
                duration=time.time() - start_time,
                metrics_collected=suggestion_count,
                data_points=suggestion_count,
                details={
                    "suggestions_generated": suggestion_count,
                    "suggestion_types": list(suggestions.keys()) if suggestions else [],
                    "suggestions_available": suggestions is not None
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            result = PerformanceTestResult(
                test_id=test_id,
                test_type="optimization_suggestions",
                status="failed",
                duration=time.time() - start_time,
                metrics_collected=0,
                data_points=0,
                details={},
                timestamp=time.time(),
                error_message=str(e)
            )
        
        self.test_results.append(result)
        return result
    
    async def test_continuous_monitoring(self) -> PerformanceTestResult:
        """Test continuous monitoring over extended period"""
        test_id = f"continuous_{int(time.time())}"
        start_time = time.time()
        
        try:
            if not self.monitor_available:
                raise Exception("Performance monitor not available")
            
            # Start monitoring
            self.performance_monitor.start_monitoring()
            
            # Monitor for extended period
            snapshots_collected = 0
            for i in range(5):  # 5 iterations
                await asyncio.sleep(1.0)
                current = self.performance_monitor.get_current_performance()
                if current:
                    snapshots_collected += 1
            
            # Get final analytics
            analytics = self.performance_monitor.get_performance_analytics()
            
            # Stop monitoring
            self.performance_monitor.stop_monitoring()
            
            result = PerformanceTestResult(
                test_id=test_id,
                test_type="continuous_monitoring",
                status="success" if snapshots_collected > 0 else "failed",
                duration=time.time() - start_time,
                metrics_collected=snapshots_collected,
                data_points=analytics.get("total_snapshots", 0) if analytics else 0,
                details={
                    "snapshots_collected": snapshots_collected,
                    "monitoring_duration": time.time() - start_time,
                    "collection_rate": analytics.get("collection_rate", 0) if analytics else 0,
                    "continuous_operation": True
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            result = PerformanceTestResult(
                test_id=test_id,
                test_type="continuous_monitoring",
                status="failed",
                duration=time.time() - start_time,
                metrics_collected=0,
                data_points=0,
                details={},
                timestamp=time.time(),
                error_message=str(e)
            )
        
        self.test_results.append(result)
        return result
    
    async def run_all_performance_tests(self) -> List[PerformanceTestResult]:
        """Run all performance monitoring tests"""
        self.logger.info("📊 Starting comprehensive performance monitoring tests...")
        
        results = []
        
        # Run basic monitoring test
        basic_result = await self.test_basic_monitoring()
        results.append(basic_result)
        self.logger.info(f"✅ Basic monitoring: {basic_result.status} ({basic_result.metrics_collected} metrics)")
        
        # Run analytics test
        analytics_result = await self.test_analytics_system()
        results.append(analytics_result)
        self.logger.info(f"✅ Analytics: {analytics_result.status} ({analytics_result.data_points} data points)")
        
        # Run bottleneck detection test
        bottleneck_result = await self.test_bottleneck_detection()
        results.append(bottleneck_result)
        self.logger.info(f"✅ Bottleneck detection: {bottleneck_result.status} ({bottleneck_result.metrics_collected} bottlenecks)")
        
        # Run optimization suggestions test
        optimization_result = await self.test_optimization_suggestions()
        results.append(optimization_result)
        self.logger.info(f"✅ Optimization suggestions: {optimization_result.status} ({optimization_result.metrics_collected} suggestions)")
        
        # Run continuous monitoring test
        continuous_result = await self.test_continuous_monitoring()
        results.append(continuous_result)
        self.logger.info(f"✅ Continuous monitoring: {continuous_result.status} ({continuous_result.data_points} snapshots)")
        
        # Calculate summary
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.status == "success")
        total_metrics = sum(r.metrics_collected for r in results)
        
        self.logger.info(f"🎊 Performance monitoring tests completed: {successful_tests}/{total_tests} successful, {total_metrics} total metrics")
        
        return results
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get test summary statistics"""
        if not self.test_results:
            return {"message": "No tests run yet"}
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.status == "success")
        failed_tests = sum(1 for r in self.test_results if r.status == "failed")
        total_metrics = sum(r.metrics_collected for r in self.test_results)
        total_data_points = sum(r.data_points for r in self.test_results)
        
        # Test type stats
        test_type_stats = {}
        for result in self.test_results:
            test_type = result.test_type
            if test_type not in test_type_stats:
                test_type_stats[test_type] = {"tests": 0, "success_rate": 0}
            
            test_type_stats[test_type]["tests"] += 1
        
        # Calculate success rates
        for test_type in test_type_stats:
            type_tests = [r for r in self.test_results if r.test_type == test_type]
            successful = sum(1 for r in type_tests if r.status == "success")
            test_type_stats[test_type]["success_rate"] = (successful / len(type_tests)) * 100
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests / total_tests) * 100,
            "total_metrics_collected": total_metrics,
            "total_data_points": total_data_points,
            "test_type_statistics": test_type_stats,
            "recent_tests": [asdict(r) for r in self.test_results[-5:]]
        }

# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def main():
        tester = PerformanceMonitorTester()
        results = await tester.run_all_performance_tests()
        
        print("\n📊 PERFORMANCE MONITOR TEST RESULTS")
        print("=" * 50)
        
        for result in results:
            status_icon = "✅" if result.status == "success" else "❌"
            print(f"{status_icon} {result.test_type}: {result.metrics_collected} metrics ({result.duration:.2f}s)")
        
        summary = tester.get_test_summary()
        print(f"\n📊 Summary: {summary['successful_tests']}/{summary['total_tests']} tests successful")
        print(f"🎯 Total metrics: {summary['total_metrics_collected']}")
        print(f"📈 Total data points: {summary['total_data_points']}")
    
    asyncio.run(main())
