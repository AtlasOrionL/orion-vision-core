#!/usr/bin/env python3
"""
📱 Orion Vision Core - Mobile Foundation Test Suite
Comprehensive testing for mobile app foundation

This test suite covers:
- Mobile App Foundation functionality
- Cross-Platform Manager capabilities
- Mobile UI Framework features
- Touch gesture recognition
- Platform adaptation and optimization

Sprint 9.2: Mobile Integration and Cross-Platform
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mobile.mobile_app_foundation import (
    MobileAppFoundation, MobileConfig, PlatformType, AppState, 
    DeviceCapability, DeviceInfo
)
from mobile.cross_platform_manager import (
    CrossPlatformManager, AdaptationStrategy, PerformanceProfile
)
from mobile.mobile_ui_framework import (
    MobileUIFramework, ComponentType, GestureType, ThemeMode, LayoutType
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MobileFoundationTestSuite:
    """Test suite for mobile foundation capabilities"""
    
    def __init__(self):
        self.test_results = {}
    
    async def test_mobile_app_foundation(self):
        """Test Mobile App Foundation functionality"""
        logger.info("📱 Testing Mobile App Foundation...")
        
        try:
            # Initialize mobile app foundation
            config = MobileConfig(
                app_name="Orion Test App",
                app_version="9.2.0",
                platform=PlatformType.PWA,
                offline_enabled=True,
                push_notifications_enabled=True,
                biometric_auth_enabled=True
            )
            
            foundation = MobileAppFoundation(config)
            
            # Test initialization
            init_success = await foundation.initialize()
            if not init_success:
                raise Exception("Foundation initialization failed")
            
            # Test device info detection
            device_info = foundation.get_device_info()
            if not device_info:
                raise Exception("Device info not detected")
            
            # Test capability checking
            camera_available = foundation.is_capability_available(DeviceCapability.CAMERA)
            biometric_available = foundation.is_capability_available(DeviceCapability.BIOMETRIC)
            
            # Test permission requests
            camera_permission = await foundation.request_permission(DeviceCapability.CAMERA)
            
            # Test lifecycle handlers
            lifecycle_handler_called = False
            
            async def test_lifecycle_handler(old_state, new_state):
                nonlocal lifecycle_handler_called
                lifecycle_handler_called = True
                logger.info(f"📡 Lifecycle: {old_state.value} → {new_state.value}")
            
            foundation.register_lifecycle_handler(AppState.BACKGROUND, test_lifecycle_handler)
            
            # Test app state changes
            await foundation.handle_app_pause()
            await foundation.handle_app_resume()
            
            # Test metrics collection
            metrics = foundation.get_app_metrics()
            if metrics.startup_time <= 0:
                raise Exception("Metrics not collected properly")
            
            # Test platform adapter
            adapter = foundation.get_platform_adapter()
            if not adapter:
                raise Exception("Platform adapter not available")
            
            # Test foundation info
            foundation_info = foundation.get_foundation_info()
            if not foundation_info:
                raise Exception("Foundation info not available")
            
            self.test_results['mobile_app_foundation'] = {
                'success': True,
                'operations_tested': 10,
                'device_info': {
                    'platform': device_info.platform.value,
                    'capabilities_count': len(device_info.capabilities),
                    'memory_mb': device_info.available_memory
                },
                'capabilities': {
                    'camera_available': camera_available,
                    'biometric_available': biometric_available,
                    'camera_permission': camera_permission
                },
                'lifecycle_handler_called': lifecycle_handler_called,
                'metrics': {
                    'startup_time': metrics.startup_time,
                    'memory_usage': metrics.memory_usage
                },
                'foundation_info': foundation_info
            }
            
            logger.info("✅ Mobile App Foundation tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Mobile App Foundation test failed: {e}")
            self.test_results['mobile_app_foundation'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_cross_platform_manager(self):
        """Test Cross-Platform Manager functionality"""
        logger.info("🌐 Testing Cross-Platform Manager...")
        
        try:
            # Initialize cross-platform manager
            manager = CrossPlatformManager()
            
            # Create test device info
            device_info = DeviceInfo(
                platform=PlatformType.PWA,
                os_version="14.0",
                device_model="Test Device",
                screen_width=375,
                screen_height=812,
                screen_density=2.0,
                available_memory=4096,
                storage_space=32768,
                capabilities=[
                    DeviceCapability.CAMERA,
                    DeviceCapability.BIOMETRIC,
                    DeviceCapability.PUSH_NOTIFICATIONS
                ]
            )
            
            # Test initialization
            init_success = await manager.initialize(device_info)
            if not init_success:
                raise Exception("Cross-platform manager initialization failed")
            
            # Test platform capabilities
            capabilities = manager.get_platform_capabilities(PlatformType.PWA)
            if not capabilities:
                raise Exception("Platform capabilities not available")
            
            # Test platform adapter
            adapter = manager.get_platform_adapter(PlatformType.IOS)
            if not adapter:
                raise Exception("Platform adapter not available")
            
            # Test feature support checking
            storage_supported = manager.is_feature_supported("IndexedDB", PlatformType.PWA)
            camera_supported = manager.is_feature_supported("Camera", PlatformType.IOS)
            
            # Test unified API calls
            storage_result = await manager.call_unified_api("storage", "save", data="test")
            networking_result = await manager.call_unified_api("networking", "get", url="test")
            
            # Test supported platforms
            supported_platforms = manager.get_supported_platforms()
            if len(supported_platforms) < 3:
                raise Exception("Insufficient supported platforms")
            
            # Test platform metrics
            metrics = manager.get_platform_metrics()
            if not metrics:
                raise Exception("Platform metrics not available")
            
            # Test manager info
            manager_info = manager.get_manager_info()
            if not manager_info:
                raise Exception("Manager info not available")
            
            self.test_results['cross_platform_manager'] = {
                'success': True,
                'operations_tested': 9,
                'supported_platforms': [p.value for p in supported_platforms],
                'capabilities_tested': {
                    'pwa_capabilities': len(capabilities.storage_options) if capabilities else 0,
                    'storage_supported': storage_supported,
                    'camera_supported': camera_supported
                },
                'unified_api_results': {
                    'storage_result': storage_result,
                    'networking_result': networking_result
                },
                'platform_metrics': metrics,
                'manager_info': manager_info
            }
            
            logger.info("✅ Cross-Platform Manager tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cross-Platform Manager test failed: {e}")
            self.test_results['cross_platform_manager'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_mobile_ui_framework(self):
        """Test Mobile UI Framework functionality"""
        logger.info("📱 Testing Mobile UI Framework...")
        
        try:
            # Initialize mobile UI framework
            ui_framework = MobileUIFramework(PlatformType.IOS)
            
            # Test initialization
            init_success = await ui_framework.initialize(375, 812, 2.0)
            if not init_success:
                raise Exception("UI Framework initialization failed")
            
            # Test component creation
            button = ui_framework.create_component(
                "test_button",
                ComponentType.BUTTON,
                x=50, y=100, width=200, height=44,
                title="Test Button"
            )
            
            text_input = ui_framework.create_component(
                "test_input",
                ComponentType.TEXT_INPUT,
                x=50, y=200, width=200, height=44,
                placeholder="Enter text"
            )
            
            # Test layout creation
            layout = ui_framework.create_layout(
                "main_layout",
                LayoutType.LINEAR,
                [button, text_input]
            )
            
            # Test theme switching
            available_themes = ui_framework.get_available_themes()
            if len(available_themes) < 2:
                raise Exception("Insufficient themes available")
            
            theme_switch_success = await ui_framework.switch_theme("dark")
            if not theme_switch_success:
                raise Exception("Theme switch failed")
            
            # Test touch event processing
            await ui_framework.process_touch_event(100, 120, GestureType.TAP)
            await ui_framework.process_touch_event(100, 120, GestureType.SWIPE_LEFT)
            
            # Test component retrieval
            retrieved_button = ui_framework.get_component("test_button")
            if not retrieved_button:
                raise Exception("Component retrieval failed")
            
            # Test layout retrieval
            retrieved_layout = ui_framework.get_layout("main_layout")
            if not retrieved_layout:
                raise Exception("Layout retrieval failed")
            
            # Test current theme
            current_theme = ui_framework.get_current_theme()
            if not current_theme or current_theme.theme_id != "dark":
                raise Exception("Current theme not correct")
            
            # Test screen info
            screen_info = ui_framework.get_screen_info()
            if screen_info["width"] != 375 or screen_info["height"] != 812:
                raise Exception("Screen info not correct")
            
            # Test UI metrics
            ui_metrics = ui_framework.get_ui_metrics()
            if ui_metrics["total_components"] != 2:
                raise Exception("UI metrics not correct")
            
            # Test framework info
            framework_info = ui_framework.get_framework_info()
            if not framework_info:
                raise Exception("Framework info not available")
            
            self.test_results['mobile_ui_framework'] = {
                'success': True,
                'operations_tested': 12,
                'components_created': 2,
                'layouts_created': 1,
                'available_themes': available_themes,
                'theme_switch_success': theme_switch_success,
                'current_theme': current_theme.theme_id if current_theme else None,
                'screen_info': screen_info,
                'ui_metrics': ui_metrics,
                'framework_info': framework_info
            }
            
            logger.info("✅ Mobile UI Framework tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Mobile UI Framework test failed: {e}")
            self.test_results['mobile_ui_framework'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_touch_gesture_recognition(self):
        """Test touch gesture recognition"""
        logger.info("👆 Testing Touch Gesture Recognition...")
        
        try:
            # Initialize UI framework for touch testing
            ui_framework = MobileUIFramework(PlatformType.ANDROID)
            await ui_framework.initialize(360, 640, 2.0)
            
            # Test gesture handler registration
            gesture_events = []
            
            async def test_gesture_handler(event):
                gesture_events.append(event.gesture_type.value)
            
            touch_handler = ui_framework.touch_handler
            touch_handler.register_gesture_handler(GestureType.TAP, test_gesture_handler)
            touch_handler.register_gesture_handler(GestureType.SWIPE_LEFT, test_gesture_handler)
            touch_handler.register_gesture_handler(GestureType.LONG_PRESS, test_gesture_handler)
            
            # Test different gestures
            gestures_to_test = [
                GestureType.TAP,
                GestureType.DOUBLE_TAP,
                GestureType.LONG_PRESS,
                GestureType.SWIPE_LEFT,
                GestureType.SWIPE_RIGHT,
                GestureType.SWIPE_UP,
                GestureType.SWIPE_DOWN
            ]
            
            for gesture in gestures_to_test:
                await ui_framework.process_touch_event(180, 320, gesture)
            
            # Test gesture recognition parameters
            original_tap_threshold = touch_handler.tap_threshold
            touch_handler.tap_threshold = 0.5
            
            original_swipe_threshold = touch_handler.swipe_threshold
            touch_handler.swipe_threshold = 100.0
            
            # Test gesture recognition enable/disable
            touch_handler.gesture_recognition_enabled = False
            await ui_framework.process_touch_event(180, 320, GestureType.TAP)
            
            touch_handler.gesture_recognition_enabled = True
            await ui_framework.process_touch_event(180, 320, GestureType.TAP)
            
            # Restore original values
            touch_handler.tap_threshold = original_tap_threshold
            touch_handler.swipe_threshold = original_swipe_threshold
            
            # Test touch history
            touch_history_size = len(touch_handler.touch_history)
            
            self.test_results['touch_gesture_recognition'] = {
                'success': True,
                'operations_tested': 8,
                'gestures_tested': len(gestures_to_test),
                'gesture_events_captured': len(gesture_events),
                'touch_history_size': touch_history_size,
                'gesture_recognition_enabled': touch_handler.gesture_recognition_enabled,
                'thresholds': {
                    'tap_threshold': touch_handler.tap_threshold,
                    'long_press_threshold': touch_handler.long_press_threshold,
                    'swipe_threshold': touch_handler.swipe_threshold
                }
            }
            
            logger.info("✅ Touch Gesture Recognition tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Touch Gesture Recognition test failed: {e}")
            self.test_results['touch_gesture_recognition'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def run_all_tests(self):
        """Run all mobile foundation tests"""
        logger.info("📱 Starting Mobile Foundation Test Suite...")
        logger.info("=" * 80)
        
        test_results = {}
        
        # Run all test categories
        test_results['mobile_app_foundation'] = await self.test_mobile_app_foundation()
        logger.info("=" * 80)
        
        test_results['cross_platform_manager'] = await self.test_cross_platform_manager()
        logger.info("=" * 80)
        
        test_results['mobile_ui_framework'] = await self.test_mobile_ui_framework()
        logger.info("=" * 80)
        
        test_results['touch_gesture_recognition'] = await self.test_touch_gesture_recognition()
        logger.info("=" * 80)
        
        # Calculate overall success rate
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        overall_success_rate = passed_tests / total_tests
        
        logger.info("📊 MOBILE FOUNDATION TEST RESULTS:")
        logger.info(f"  Mobile App Foundation: {'✅ PASSED' if test_results['mobile_app_foundation'] else '❌ FAILED'}")
        logger.info(f"  Cross-Platform Manager: {'✅ PASSED' if test_results['cross_platform_manager'] else '❌ FAILED'}")
        logger.info(f"  Mobile UI Framework: {'✅ PASSED' if test_results['mobile_ui_framework'] else '❌ FAILED'}")
        logger.info(f"  Touch Gesture Recognition: {'✅ PASSED' if test_results['touch_gesture_recognition'] else '❌ FAILED'}")
        logger.info(f"  Overall Success Rate: {overall_success_rate:.1%}")
        
        return overall_success_rate >= 0.8, self.test_results

async def main():
    """Main test execution"""
    test_suite = MobileFoundationTestSuite()
    
    try:
        success, detailed_results = await test_suite.run_all_tests()
        
        if success:
            logger.info("🎉 MOBILE FOUNDATION TEST SUITE: ALL TESTS PASSED!")
            return True
        else:
            logger.error("❌ MOBILE FOUNDATION TEST SUITE: SOME TESTS FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
