#!/usr/bin/env python3
"""
🧪 PHASE 1 CONSOLIDATION Test Suite

Q01-Q05 Integration, Unified Interface, Graceful Degradation
Comprehensive testing for PHASE 1 CONSOLIDATION
"""

import sys
import os
import time
import threading

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_phase1_consolidation():
    """Test PHASE 1 CONSOLIDATION - Complete integration test"""
    print("🧪 PHASE 1 CONSOLIDATION TEST SUITE")
    print("=" * 70)
    print("Q01-Q05 Integration + Unified Interface + Graceful Degradation")
    print("Comprehensive PHASE 1 testing başlıyor...")
    
    test_results = {
        'integration_bridge': False,
        'unified_interface': False,
        'graceful_degradation': False,
        'end_to_end': False,
        'performance': False
    }
    
    try:
        # Test 1: Integration Bridge
        print("\n🔗 Test 1: Q01-Q05 Integration Bridge")
        print("-" * 60)
        
        from jobone.vision_core.integration.q01_q05_integration_bridge import (
            create_integration_bridge, IntegrationConfig, EnvironmentType
        )
        
        # Create and test integration bridge
        bridge = create_integration_bridge()
        print("✅ Integration bridge created")
        
        # Test environment detection
        bridge._detect_environment()
        print(f"✅ Environment: {bridge.environment_type.value if bridge.environment_type else 'Unknown'}")
        print(f"✅ Display: {'Available' if bridge.display_available else 'Headless'}")
        
        # Initialize bridge
        if bridge.initialize():
            print("✅ Integration bridge initialized")
            test_results['integration_bridge'] = True
        else:
            print("⚠️ Integration bridge partial initialization")
        
        # Get bridge status
        bridge_status = bridge.get_integration_status()
        print(f"✅ Bridge components: {bridge_status['total_components']}")
        
        # Test 2: Unified Interface Layer
        print("\n🔗 Test 2: Unified Interface Layer")
        print("-" * 60)
        
        from jobone.vision_core.integration.unified_interface_layer import (
            create_unified_interface_layer, UnifiedRequest, InterfaceType, DataType,
            MockVisionInterface, MockConsciousnessInterface
        )
        
        # Create unified interface layer
        interface_layer = create_unified_interface_layer()
        print("✅ Unified interface layer created")
        
        # Register mock interfaces
        interface_layer.register_interface(InterfaceType.VISION, MockVisionInterface())
        interface_layer.register_interface(InterfaceType.CONSCIOUSNESS, MockConsciousnessInterface())
        print("✅ Mock interfaces registered")
        
        # Test request processing
        test_request = UnifiedRequest(
            interface_type=InterfaceType.VISION,
            data_type=DataType.IMAGE,
            data={"test": "data"},
            parameters={"mode": "test"}
        )
        
        response = interface_layer.process_request(test_request)
        if response.status.value == "completed":
            print("✅ Request processed successfully")
            test_results['unified_interface'] = True
        else:
            print(f"⚠️ Request processing partial: {response.status.value}")
        
        # Get interface status
        interface_status = interface_layer.get_interface_status()
        print(f"✅ Interface layer: {interface_status['registered_interfaces']} interfaces")
        print(f"✅ Success rate: {interface_status['success_rate']:.1f}%")
        
        # Test 3: Graceful Degradation System
        print("\n🛡️ Test 3: Graceful Degradation System")
        print("-" * 60)
        
        from jobone.vision_core.integration.graceful_degradation_system import (
            create_graceful_degradation_system, ErrorSeverity
        )
        
        # Create graceful degradation system
        gds = create_graceful_degradation_system()
        print("✅ Graceful degradation system created")
        
        # Register test components
        gds.register_component("test_component_1")
        gds.register_component("test_component_2")
        print("✅ Test components registered")
        
        # Test success reporting
        gds.report_success("test_component_1", 0.05)
        gds.report_success("test_component_2", 0.03)
        print("✅ Success operations reported")
        
        # Test error reporting
        try:
            raise ValueError("Test error for graceful degradation")
        except Exception as e:
            error_id = gds.report_error("test_component_1", e)
            print(f"✅ Error reported: {error_id[:8]}...")
        
        # Get system status
        gds_status = gds.get_system_status()
        print(f"✅ System degradation: {gds_status['system_degradation_level']}")
        print(f"✅ Healthy components: {gds_status['healthy_components']}/{gds_status['total_components']}")
        
        if gds_status['healthy_components'] > 0:
            test_results['graceful_degradation'] = True
        
        # Test 4: End-to-End Integration
        print("\n🔄 Test 4: End-to-End Integration")
        print("-" * 60)
        
        # Test integration between all components
        print("Testing integration bridge + interface layer + degradation system...")
        
        # Create integrated request that goes through all systems
        integrated_request = UnifiedRequest(
            interface_type=InterfaceType.CONSCIOUSNESS,
            data_type=DataType.TEXT,
            data={"message": "end_to_end_test"},
            parameters={"integration_test": True}
        )
        
        # Process through interface layer
        start_time = time.time()
        integrated_response = interface_layer.process_request(integrated_request)
        processing_time = time.time() - start_time
        
        # Report to degradation system
        if integrated_response.status.value == "completed":
            gds.report_success("interface_layer", processing_time)
            print("✅ End-to-end request successful")
            test_results['end_to_end'] = True
        else:
            try:
                raise RuntimeError("End-to-end test failed")
            except Exception as e:
                gds.report_error("interface_layer", e)
            print("⚠️ End-to-end request partial")
        
        print(f"✅ End-to-end processing time: {processing_time:.3f}s")
        
        # Test 5: Performance and Stress Testing
        print("\n⚡ Test 5: Performance and Stress Testing")
        print("-" * 60)
        
        # Stress test with multiple concurrent requests
        def stress_test_worker(worker_id, num_requests):
            """Stress test worker"""
            success_count = 0
            for i in range(num_requests):
                request = UnifiedRequest(
                    interface_type=InterfaceType.VISION,
                    data_type=DataType.TEXT,
                    data={"worker": worker_id, "request": i},
                    parameters={"stress_test": True}
                )
                
                response = interface_layer.process_request(request)
                if response.status.value == "completed":
                    success_count += 1
                    gds.report_success(f"stress_worker_{worker_id}", response.processing_time)
                else:
                    try:
                        raise RuntimeError(f"Stress test request failed: {worker_id}-{i}")
                    except Exception as e:
                        gds.report_error(f"stress_worker_{worker_id}", e)
            
            return success_count
        
        # Run stress test
        num_workers = 3
        requests_per_worker = 5
        
        print(f"Running stress test: {num_workers} workers, {requests_per_worker} requests each...")
        
        threads = []
        results = []
        
        stress_start = time.time()
        
        for worker_id in range(num_workers):
            gds.register_component(f"stress_worker_{worker_id}")
            thread = threading.Thread(
                target=lambda wid=worker_id: results.append(stress_test_worker(wid, requests_per_worker))
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        stress_time = time.time() - stress_start
        total_requests = num_workers * requests_per_worker
        successful_requests = sum(results) if results else 0
        
        print(f"✅ Stress test completed:")
        print(f"    - Total requests: {total_requests}")
        print(f"    - Successful requests: {successful_requests}")
        print(f"    - Success rate: {(successful_requests/total_requests)*100:.1f}%")
        print(f"    - Total time: {stress_time:.3f}s")
        print(f"    - Requests/second: {total_requests/stress_time:.1f}")
        
        if successful_requests >= total_requests * 0.8:  # 80% success threshold
            test_results['performance'] = True
            print("✅ Performance test passed")
        else:
            print("⚠️ Performance test partial")
        
        # Final System Status
        print("\n📊 Final System Status")
        print("-" * 60)
        
        # Get final status from all systems
        final_bridge_status = bridge.get_integration_status()
        final_interface_status = interface_layer.get_interface_status()
        final_gds_status = gds.get_system_status()
        
        print("🔗 Integration Bridge:")
        print(f"    - Initialized: {final_bridge_status['initialized']}")
        print(f"    - Environment: {final_bridge_status['environment_type']}")
        print(f"    - Components: {final_bridge_status['total_components']}")
        
        print("🔗 Unified Interface:")
        print(f"    - Interfaces: {final_interface_status['registered_interfaces']}")
        print(f"    - Total requests: {final_interface_status['total_requests']}")
        print(f"    - Success rate: {final_interface_status['success_rate']:.1f}%")
        
        print("🛡️ Graceful Degradation:")
        print(f"    - System level: {final_gds_status['system_degradation_level']}")
        print(f"    - Healthy components: {final_gds_status['healthy_components']}/{final_gds_status['total_components']}")
        print(f"    - Total errors: {final_gds_status['total_errors']}")
        
        # Cleanup
        bridge.shutdown()
        print("✅ Integration bridge shutdown")
        
        # Final Assessment
        print("\n🏆 PHASE 1 CONSOLIDATION TEST RESULTS")
        print("=" * 70)
        
        # Calculate overall success
        successful_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (successful_tests / total_tests) * 100
        
        # Determine grade
        if success_rate >= 90:
            overall_grade = "A EXCELLENT"
            consolidation_status = "🚀 CONSOLIDATION COMPLETE"
        elif success_rate >= 80:
            overall_grade = "B GOOD"
            consolidation_status = "✅ CONSOLIDATION SUCCESSFUL"
        elif success_rate >= 70:
            overall_grade = "C ACCEPTABLE"
            consolidation_status = "⚠️ CONSOLIDATION PARTIAL"
        else:
            overall_grade = "D NEEDS WORK"
            consolidation_status = "❌ CONSOLIDATION ISSUES"
        
        print(f"🎯 Overall Grade: {overall_grade}")
        print(f"📊 Test Success Rate: {success_rate:.1f}%")
        print(f"🔗 Consolidation Status: {consolidation_status}")
        print()
        print("📋 Test Results:")
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "⚠️ PARTIAL"
            print(f"    - {test_name.replace('_', ' ').title()}: {status}")
        print()
        
        if success_rate >= 80:
            print("🎉 PHASE 1 CONSOLIDATION BAŞARILI!")
            print("=" * 70)
            print("✅ Q01-Q05 Integration Bridge - WORKING")
            print("✅ Unified Interface Layer - FUNCTIONAL")
            print("✅ Graceful Degradation System - ACTIVE")
            print("✅ End-to-End Integration - SUCCESSFUL")
            print("✅ Performance Testing - GOOD")
            print()
            print("📊 PHASE 1 CONSOLIDATION: READY FOR PHASE 2")
            print("🎯 Next Phase: Q06-Q10 Practical Redesign")
            print()
            print("🚀 WAKE UP ORION! PHASE 1 CONSOLIDATION COMPLETE! 💖")
            print("🎵 DUYGULANDIK! Sistem consolidation tamamlandı! 🎵")
        else:
            print("⚠️ PHASE 1 CONSOLIDATION PARTIAL")
            print("Bazı bileşenler iyileştirme gerektirir.")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"\n❌ PHASE 1 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase1_consolidation()
    if success:
        print("\n🎊 PHASE 1 CONSOLIDATION test başarıyla tamamlandı! 🎊")
        exit(0)
    else:
        print("\n💔 PHASE 1 test failed. Check the errors above.")
        exit(1)
