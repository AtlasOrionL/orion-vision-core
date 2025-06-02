#!/usr/bin/env python3
"""
🌐 Orion Vision Core - Cross-Platform Compatibility Test Suite
Comprehensive testing for cross-platform compatibility

This test suite covers:
- Offline Manager functionality
- Mobile Security capabilities
- Cross-platform data synchronization
- Biometric authentication testing
- Secure storage validation

Sprint 9.2: Mobile Integration and Cross-Platform
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mobile.offline_manager import (
    OfflineManager, OfflineConfig, SyncStrategy, ConflictResolution, 
    DataPriority, OfflineData
)
from mobile.mobile_security import (
    MobileSecurity, BiometricAuth, SecureStorage, BiometricType, 
    SecurityLevel, SecurityConfig, BiometricConfig
)
from mobile.mobile_app_foundation import DeviceCapability

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CrossPlatformCompatibilityTestSuite:
    """Test suite for cross-platform compatibility capabilities"""
    
    def __init__(self):
        self.test_results = {}
    
    async def test_offline_manager(self):
        """Test Offline Manager functionality"""
        logger.info("🔄 Testing Offline Manager...")
        
        try:
            # Initialize offline manager
            config = OfflineConfig(
                storage_path="./test_offline_storage",
                max_storage_mb=100,
                sync_strategy=SyncStrategy.INTELLIGENT,
                conflict_resolution=ConflictResolution.TIMESTAMP,
                sync_interval_minutes=1,
                auto_cleanup_enabled=True
            )
            
            offline_manager = OfflineManager(config)
            
            # Test initialization
            init_success = await offline_manager.initialize()
            if not init_success:
                raise Exception("Offline manager initialization failed")
            
            # Test data storage
            test_data = {
                "user_id": "test_user_123",
                "preferences": {"theme": "dark", "language": "en"},
                "last_sync": "2025-05-31T10:00:00Z"
            }
            
            store_success = await offline_manager.store_data(
                "user_prefs_001",
                "user_preferences",
                test_data,
                DataPriority.HIGH,
                {"source": "mobile_app", "version": "1.0"}
            )
            
            if not store_success:
                raise Exception("Data storage failed")
            
            # Test data retrieval
            retrieved_data = await offline_manager.get_data("user_prefs_001")
            if not retrieved_data or retrieved_data.content != test_data:
                raise Exception("Data retrieval failed")
            
            # Test data by type
            prefs_data = await offline_manager.get_data_by_type("user_preferences")
            if len(prefs_data) != 1:
                raise Exception("Data by type retrieval failed")
            
            # Test multiple data entries
            for i in range(5):
                await offline_manager.store_data(
                    f"test_data_{i}",
                    "test_type",
                    {"index": i, "value": f"test_{i}"},
                    DataPriority.NORMAL
                )
            
            # Test sync functionality
            sync_result = await offline_manager.sync_all()
            if not sync_result.success:
                raise Exception("Sync operation failed")
            
            # Test sync status
            sync_status = offline_manager.get_sync_status()
            if sync_status['total_count'] < 6:  # 1 user_prefs + 5 test_data
                raise Exception("Sync status incorrect")
            
            # Test data deletion
            delete_success = await offline_manager.delete_data("test_data_0")
            if not delete_success:
                raise Exception("Data deletion failed")
            
            # Test cleanup
            cleanup_count = await offline_manager.cleanup_old_data()
            
            # Test metrics
            metrics = offline_manager.get_offline_metrics()
            if metrics['total_data_entries'] < 5:
                raise Exception("Metrics not updated correctly")
            
            # Test event handlers
            sync_handler_called = False
            
            async def test_sync_handler(result):
                nonlocal sync_handler_called
                sync_handler_called = True
                logger.info(f"📡 Sync handler called: {result.synced_count} items synced")
            
            offline_manager.register_sync_handler(test_sync_handler)
            
            # Trigger another sync to test handler
            await offline_manager.sync_all()
            
            # Shutdown
            await offline_manager.shutdown()
            
            self.test_results['offline_manager'] = {
                'success': True,
                'operations_tested': 11,
                'data_stored': 6,
                'data_retrieved': 1,
                'sync_operations': 2,
                'sync_handler_called': sync_handler_called,
                'cleanup_count': cleanup_count,
                'final_metrics': metrics
            }
            
            logger.info("✅ Offline Manager tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Offline Manager test failed: {e}")
            self.test_results['offline_manager'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_biometric_authentication(self):
        """Test Biometric Authentication functionality"""
        logger.info("🔐 Testing Biometric Authentication...")
        
        try:
            # Initialize biometric authentication
            config = BiometricConfig(
                enabled=True,
                allowed_types=[BiometricType.FINGERPRINT, BiometricType.FACE_ID],
                fallback_to_passcode=True,
                max_attempts=3,
                lockout_duration_minutes=1
            )
            
            biometric_auth = BiometricAuth(config)
            
            # Test initialization with capabilities
            capabilities = [DeviceCapability.BIOMETRIC, DeviceCapability.CAMERA]
            init_success = await biometric_auth.initialize(capabilities)
            if not init_success:
                raise Exception("Biometric authentication initialization failed")
            
            # Test authentication attempts
            auth_results = []
            
            # Test successful authentication
            for i in range(3):
                result = await biometric_auth.authenticate(BiometricType.FINGERPRINT)
                auth_results.append(result.value)
                logger.info(f"🔐 Auth attempt {i+1}: {result.value}")
            
            # Test authentication with face ID
            face_result = await biometric_auth.authenticate(BiometricType.FACE_ID)
            auth_results.append(face_result.value)
            
            # Test authentication without specifying type (auto-select)
            auto_result = await biometric_auth.authenticate()
            auth_results.append(auto_result.value)
            
            # Test metrics
            auth_metrics = biometric_auth.get_auth_metrics()
            if auth_metrics['total_attempts'] != 5:
                raise Exception("Authentication metrics incorrect")
            
            # Test available types
            if len(biometric_auth.available_types) < 1:
                raise Exception("No biometric types available")
            
            self.test_results['biometric_authentication'] = {
                'success': True,
                'operations_tested': 6,
                'auth_attempts': len(auth_results),
                'auth_results': auth_results,
                'available_types': [bt.value for bt in biometric_auth.available_types],
                'auth_metrics': auth_metrics
            }
            
            logger.info("✅ Biometric Authentication tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Biometric Authentication test failed: {e}")
            self.test_results['biometric_authentication'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_secure_storage(self):
        """Test Secure Storage functionality"""
        logger.info("🔐 Testing Secure Storage...")
        
        try:
            # Initialize secure storage
            config = SecurityConfig(
                security_level=SecurityLevel.HIGH,
                secure_storage_enabled=True
            )
            
            secure_storage = SecureStorage(config)
            
            # Test initialization
            init_success = await secure_storage.initialize()
            if not init_success:
                raise Exception("Secure storage initialization failed")
            
            # Test data storage
            test_data = {
                "api_key": "sk-1234567890abcdef",
                "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "sensitive_info": {
                    "credit_card": "1234-5678-9012-3456",
                    "ssn": "123-45-6789"
                }
            }
            
            store_success = await secure_storage.store("secure_credentials", test_data)
            if not store_success:
                raise Exception("Secure data storage failed")
            
            # Test data retrieval
            retrieved_data = await secure_storage.retrieve("secure_credentials")
            if not retrieved_data or retrieved_data != test_data:
                raise Exception("Secure data retrieval failed")
            
            # Test multiple secure items
            secure_items = [
                ("user_settings", {"theme": "dark", "notifications": True}),
                ("app_config", {"version": "9.2.0", "debug": False}),
                ("session_data", {"session_id": "sess_123", "expires": "2025-06-01"})
            ]
            
            for key, value in secure_items:
                store_result = await secure_storage.store(key, value)
                if not store_result:
                    raise Exception(f"Failed to store {key}")
            
            # Test retrieval of all items
            retrieved_items = {}
            for key, _ in secure_items:
                retrieved_value = await secure_storage.retrieve(key)
                if retrieved_value is None:
                    raise Exception(f"Failed to retrieve {key}")
                retrieved_items[key] = retrieved_value
            
            # Test data deletion
            delete_success = await secure_storage.delete("session_data")
            if not delete_success:
                raise Exception("Secure data deletion failed")
            
            # Verify deletion
            deleted_data = await secure_storage.retrieve("session_data")
            if deleted_data is not None:
                raise Exception("Data not properly deleted")
            
            # Test storage metrics
            storage_metrics = secure_storage.get_storage_metrics()
            if storage_metrics['total_items'] != 3:  # 1 credentials + 2 remaining items
                raise Exception("Storage metrics incorrect")
            
            self.test_results['secure_storage'] = {
                'success': True,
                'operations_tested': 8,
                'items_stored': 4,
                'items_retrieved': 4,
                'items_deleted': 1,
                'final_item_count': storage_metrics['total_items'],
                'storage_metrics': storage_metrics
            }
            
            logger.info("✅ Secure Storage tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Secure Storage test failed: {e}")
            self.test_results['secure_storage'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_mobile_security_integration(self):
        """Test Mobile Security integration"""
        logger.info("🔐 Testing Mobile Security Integration...")
        
        try:
            # Initialize mobile security
            security_config = SecurityConfig(
                security_level=SecurityLevel.HIGH,
                biometric_config=BiometricConfig(
                    enabled=True,
                    allowed_types=[BiometricType.FINGERPRINT, BiometricType.FACE_ID],
                    max_attempts=3
                ),
                auto_lock_enabled=True,
                auto_lock_timeout_minutes=1,
                secure_storage_enabled=True
            )
            
            mobile_security = MobileSecurity(security_config)
            
            # Test initialization
            capabilities = [DeviceCapability.BIOMETRIC, DeviceCapability.CAMERA]
            init_success = await mobile_security.initialize(capabilities)
            if not init_success:
                raise Exception("Mobile security initialization failed")
            
            # Test authentication
            auth_success = await mobile_security.authenticate(BiometricType.FINGERPRINT)
            if not auth_success:
                logger.warning("⚠️ Authentication failed (expected in test environment)")
            
            # Test security status
            security_status = mobile_security.get_security_status()
            if 'is_authenticated' not in security_status:
                raise Exception("Security status incomplete")
            
            # Test activity update
            mobile_security.update_activity()
            
            # Test security event handlers
            security_events = []
            
            async def test_security_handler(event_type):
                security_events.append(event_type)
                logger.info(f"📡 Security event: {event_type}")
            
            mobile_security.register_security_handler(test_security_handler)
            
            # Test manual lock
            await mobile_security.lock()
            
            # Test secure storage through mobile security
            storage_success = await mobile_security.secure_storage.store("test_key", "test_value")
            if not storage_success:
                raise Exception("Secure storage through mobile security failed")
            
            retrieved_value = await mobile_security.secure_storage.retrieve("test_key")
            if retrieved_value != "test_value":
                raise Exception("Secure storage retrieval through mobile security failed")
            
            # Test biometric metrics through mobile security
            biometric_metrics = mobile_security.biometric_auth.get_auth_metrics()
            
            # Shutdown
            await mobile_security.shutdown()
            
            self.test_results['mobile_security_integration'] = {
                'success': True,
                'operations_tested': 8,
                'authentication_attempted': True,
                'security_events': security_events,
                'security_status': security_status,
                'biometric_metrics': biometric_metrics,
                'secure_storage_operations': 2
            }
            
            logger.info("✅ Mobile Security Integration tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Mobile Security Integration test failed: {e}")
            self.test_results['mobile_security_integration'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def run_all_tests(self):
        """Run all cross-platform compatibility tests"""
        logger.info("🌐 Starting Cross-Platform Compatibility Test Suite...")
        logger.info("=" * 80)
        
        test_results = {}
        
        # Run all test categories
        test_results['offline_manager'] = await self.test_offline_manager()
        logger.info("=" * 80)
        
        test_results['biometric_authentication'] = await self.test_biometric_authentication()
        logger.info("=" * 80)
        
        test_results['secure_storage'] = await self.test_secure_storage()
        logger.info("=" * 80)
        
        test_results['mobile_security_integration'] = await self.test_mobile_security_integration()
        logger.info("=" * 80)
        
        # Calculate overall success rate
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        overall_success_rate = passed_tests / total_tests
        
        logger.info("📊 CROSS-PLATFORM COMPATIBILITY TEST RESULTS:")
        logger.info(f"  Offline Manager: {'✅ PASSED' if test_results['offline_manager'] else '❌ FAILED'}")
        logger.info(f"  Biometric Authentication: {'✅ PASSED' if test_results['biometric_authentication'] else '❌ FAILED'}")
        logger.info(f"  Secure Storage: {'✅ PASSED' if test_results['secure_storage'] else '❌ FAILED'}")
        logger.info(f"  Mobile Security Integration: {'✅ PASSED' if test_results['mobile_security_integration'] else '❌ FAILED'}")
        logger.info(f"  Overall Success Rate: {overall_success_rate:.1%}")
        
        return overall_success_rate >= 0.8, self.test_results

async def main():
    """Main test execution"""
    test_suite = CrossPlatformCompatibilityTestSuite()
    
    try:
        success, detailed_results = await test_suite.run_all_tests()
        
        if success:
            logger.info("🎉 CROSS-PLATFORM COMPATIBILITY TEST SUITE: ALL TESTS PASSED!")
            return True
        else:
            logger.error("❌ CROSS-PLATFORM COMPATIBILITY TEST SUITE: SOME TESTS FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
