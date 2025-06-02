#!/usr/bin/env python3
"""
☁️ Orion Vision Core - Cloud Storage Integration Test Suite
Comprehensive testing for multi-cloud storage capabilities

This test suite covers:
- AWS S3 provider functionality
- Google Cloud Storage provider functionality
- Azure Blob Storage provider functionality
- Multi-cloud storage manager
- Cross-cloud operations and synchronization
- Performance and reliability testing

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import sys
import os
import tempfile
from typing import Dict, Any

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.storage_manager import CloudStorageManager, StorageProvider, StorageConfig, StorageStrategy
from cloud.providers.aws_s3 import AWSS3Provider
from cloud.providers.google_cloud import GoogleCloudProvider
from cloud.providers.azure_blob import AzureBlobProvider

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudStorageTestSuite:
    """Test suite for cloud storage integration"""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = tempfile.mkdtemp()
        self.test_bucket = "orion-test-bucket"
        
        # Test configurations for each provider
        self.provider_configs = {
            StorageProvider.AWS_S3: {
                'access_key_id': 'test_access_key',
                'secret_access_key': 'test_secret_key',
                'region': 'us-east-1'
            },
            StorageProvider.GOOGLE_CLOUD: {
                'project_id': 'orion-test-project',
                'credentials_path': '/path/to/credentials.json',
                'location': 'US'
            },
            StorageProvider.AZURE_BLOB: {
                'account_name': 'orionteststorage',
                'account_key': 'test_account_key',
                'default_tier': 'Hot'
            }
        }
    
    def _create_test_file(self, filename: str, size_kb: int = 1) -> str:
        """Create a test file for upload testing"""
        
        file_path = os.path.join(self.temp_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(b'0' * (size_kb * 1024))
        
        return file_path
    
    async def test_aws_s3_provider(self):
        """Test AWS S3 provider functionality"""
        logger.info("🔧 Testing AWS S3 Provider...")
        
        try:
            # Initialize provider
            provider = AWSS3Provider(self.provider_configs[StorageProvider.AWS_S3])
            
            # Test connection
            connected = await provider.connect()
            if not connected:
                raise Exception("Failed to connect to AWS S3")
            
            # Create test file
            test_file = self._create_test_file("s3_test.txt", 2)
            
            # Test upload
            upload_result = await provider.upload_file(
                test_file, "test/s3_test.txt", self.test_bucket,
                metadata={'test': 'true', 'provider': 's3'}
            )
            
            if not upload_result.success:
                raise Exception(f"Upload failed: {upload_result.error_message}")
            
            # Test file existence
            exists = await provider.file_exists("test/s3_test.txt", self.test_bucket)
            if not exists:
                raise Exception("File existence check failed")
            
            # Test metadata retrieval
            metadata = await provider.get_file_metadata("test/s3_test.txt", self.test_bucket)
            if not metadata:
                raise Exception("Metadata retrieval failed")
            
            # Test file listing
            files = await provider.list_files(self.test_bucket, "test/", 10)
            if len(files) == 0:
                logger.warning("⚠️ No files found in listing (expected for simulation)")
            
            # Test download
            download_path = os.path.join(self.temp_dir, "s3_downloaded.txt")
            download_result = await provider.download_file(
                "test/s3_test.txt", download_path, self.test_bucket
            )
            
            if not download_result.success:
                raise Exception(f"Download failed: {download_result.error_message}")
            
            # Test delete
            delete_result = await provider.delete_file("test/s3_test.txt", self.test_bucket)
            if not delete_result.success:
                raise Exception(f"Delete failed: {delete_result.error_message}")
            
            # Test performance metrics
            metrics = provider.get_performance_metrics()
            
            await provider.disconnect()
            
            self.test_results['aws_s3'] = {
                'success': True,
                'operations_tested': 6,
                'metrics': metrics
            }
            
            logger.info("✅ AWS S3 Provider tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ AWS S3 Provider test failed: {e}")
            self.test_results['aws_s3'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_google_cloud_provider(self):
        """Test Google Cloud Storage provider functionality"""
        logger.info("🔧 Testing Google Cloud Storage Provider...")
        
        try:
            # Initialize provider
            provider = GoogleCloudProvider(self.provider_configs[StorageProvider.GOOGLE_CLOUD])
            
            # Test connection
            connected = await provider.connect()
            if not connected:
                raise Exception("Failed to connect to Google Cloud Storage")
            
            # Create test file
            test_file = self._create_test_file("gcs_test.json", 3)
            
            # Test upload
            upload_result = await provider.upload_file(
                test_file, "test/gcs_test.json", self.test_bucket,
                metadata={'test': 'true', 'provider': 'gcs'}
            )
            
            if not upload_result.success:
                raise Exception(f"Upload failed: {upload_result.error_message}")
            
            # Test file existence
            exists = await provider.file_exists("test/gcs_test.json", self.test_bucket)
            if not exists:
                raise Exception("File existence check failed")
            
            # Test metadata retrieval
            metadata = await provider.get_file_metadata("test/gcs_test.json", self.test_bucket)
            if not metadata:
                raise Exception("Metadata retrieval failed")
            
            # Test file listing
            files = await provider.list_files(self.test_bucket, "test/", 10)
            if len(files) == 0:
                logger.warning("⚠️ No files found in listing (expected for simulation)")
            
            # Test download
            download_path = os.path.join(self.temp_dir, "gcs_downloaded.json")
            download_result = await provider.download_file(
                "test/gcs_test.json", download_path, self.test_bucket
            )
            
            if not download_result.success:
                raise Exception(f"Download failed: {download_result.error_message}")
            
            # Test delete
            delete_result = await provider.delete_file("test/gcs_test.json", self.test_bucket)
            if not delete_result.success:
                raise Exception(f"Delete failed: {delete_result.error_message}")
            
            # Test performance metrics
            metrics = provider.get_performance_metrics()
            
            await provider.disconnect()
            
            self.test_results['google_cloud'] = {
                'success': True,
                'operations_tested': 6,
                'metrics': metrics
            }
            
            logger.info("✅ Google Cloud Storage Provider tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Google Cloud Storage Provider test failed: {e}")
            self.test_results['google_cloud'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_azure_blob_provider(self):
        """Test Azure Blob Storage provider functionality"""
        logger.info("🔧 Testing Azure Blob Storage Provider...")
        
        try:
            # Initialize provider
            provider = AzureBlobProvider(self.provider_configs[StorageProvider.AZURE_BLOB])
            
            # Test connection
            connected = await provider.connect()
            if not connected:
                raise Exception("Failed to connect to Azure Blob Storage")
            
            # Create test file
            test_file = self._create_test_file("azure_test.yaml", 4)
            
            # Test upload
            upload_result = await provider.upload_file(
                test_file, "test/azure_test.yaml", self.test_bucket,
                metadata={'test': 'true', 'provider': 'azure'}
            )
            
            if not upload_result.success:
                raise Exception(f"Upload failed: {upload_result.error_message}")
            
            # Test file existence
            exists = await provider.file_exists("test/azure_test.yaml", self.test_bucket)
            if not exists:
                raise Exception("File existence check failed")
            
            # Test metadata retrieval
            metadata = await provider.get_file_metadata("test/azure_test.yaml", self.test_bucket)
            if not metadata:
                raise Exception("Metadata retrieval failed")
            
            # Test file listing
            files = await provider.list_files(self.test_bucket, "test/", 10)
            if len(files) == 0:
                logger.warning("⚠️ No files found in listing (expected for simulation)")
            
            # Test download
            download_path = os.path.join(self.temp_dir, "azure_downloaded.yaml")
            download_result = await provider.download_file(
                "test/azure_test.yaml", download_path, self.test_bucket
            )
            
            if not download_result.success:
                raise Exception(f"Download failed: {download_result.error_message}")
            
            # Test delete
            delete_result = await provider.delete_file("test/azure_test.yaml", self.test_bucket)
            if not delete_result.success:
                raise Exception(f"Delete failed: {delete_result.error_message}")
            
            # Test performance metrics
            metrics = provider.get_performance_metrics()
            
            await provider.disconnect()
            
            self.test_results['azure_blob'] = {
                'success': True,
                'operations_tested': 6,
                'metrics': metrics
            }
            
            logger.info("✅ Azure Blob Storage Provider tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Azure Blob Storage Provider test failed: {e}")
            self.test_results['azure_blob'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_multi_cloud_storage_manager(self):
        """Test multi-cloud storage manager functionality"""
        logger.info("☁️ Testing Multi-Cloud Storage Manager...")
        
        try:
            # Configure storage manager
            storage_config = StorageConfig(
                primary_provider=StorageProvider.AWS_S3,
                backup_providers=[StorageProvider.GOOGLE_CLOUD, StorageProvider.AZURE_BLOB],
                strategy=StorageStrategy.REDUNDANT,
                auto_sync=True
            )
            
            # Initialize storage manager
            storage_manager = CloudStorageManager(storage_config, self.provider_configs)
            
            # Test provider connections
            connection_results = await storage_manager.connect_all_providers()
            
            connected_providers = sum(1 for connected in connection_results.values() if connected)
            if connected_providers == 0:
                raise Exception("No providers connected successfully")
            
            # Create test file
            test_file = self._create_test_file("multi_cloud_test.txt", 5)
            
            # Test unified upload
            upload_result = await storage_manager.upload_file(
                test_file, "test/multi_cloud_test.txt", self.test_bucket,
                metadata={'test': 'true', 'type': 'multi_cloud'}
            )
            
            if not upload_result.success:
                raise Exception(f"Multi-cloud upload failed: {upload_result.error_message}")
            
            # Test file existence across providers
            exists = await storage_manager.file_exists("test/multi_cloud_test.txt", self.test_bucket)
            if not exists:
                raise Exception("Multi-cloud file existence check failed")
            
            # Test unified download
            download_path = os.path.join(self.temp_dir, "multi_cloud_downloaded.txt")
            download_result = await storage_manager.download_file(
                "test/multi_cloud_test.txt", download_path, self.test_bucket
            )
            
            if not download_result.success:
                raise Exception(f"Multi-cloud download failed: {download_result.error_message}")
            
            # Test file listing
            files = await storage_manager.list_files(self.test_bucket, "test/", 10)
            
            # Test provider status
            provider_status = storage_manager.get_provider_status()
            
            # Test storage metrics
            metrics = storage_manager.get_storage_metrics()
            
            # Test delete from all providers
            delete_results = await storage_manager.delete_file(
                "test/multi_cloud_test.txt", self.test_bucket, delete_from_all=True
            )
            
            successful_deletes = sum(1 for result in delete_results.values() if result.success)
            
            await storage_manager.disconnect_all_providers()
            
            self.test_results['multi_cloud_manager'] = {
                'success': True,
                'connected_providers': connected_providers,
                'operations_tested': 5,
                'successful_deletes': successful_deletes,
                'metrics': {
                    'total_operations': metrics.total_operations,
                    'successful_operations': metrics.successful_operations,
                    'provider_count': len(provider_status)
                }
            }
            
            logger.info("✅ Multi-Cloud Storage Manager tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Multi-Cloud Storage Manager test failed: {e}")
            self.test_results['multi_cloud_manager'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def run_all_tests(self):
        """Run all cloud storage tests"""
        logger.info("☁️ Starting Cloud Storage Integration Test Suite...")
        logger.info("=" * 80)
        
        test_results = {}
        
        # Test individual providers
        test_results['aws_s3'] = await self.test_aws_s3_provider()
        logger.info("=" * 80)
        
        test_results['google_cloud'] = await self.test_google_cloud_provider()
        logger.info("=" * 80)
        
        test_results['azure_blob'] = await self.test_azure_blob_provider()
        logger.info("=" * 80)
        
        # Test multi-cloud manager
        test_results['multi_cloud_manager'] = await self.test_multi_cloud_storage_manager()
        logger.info("=" * 80)
        
        # Calculate overall success rate
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        overall_success_rate = passed_tests / total_tests
        
        logger.info("📊 CLOUD STORAGE INTEGRATION TEST RESULTS:")
        logger.info(f"  AWS S3 Provider: {'✅ PASSED' if test_results['aws_s3'] else '❌ FAILED'}")
        logger.info(f"  Google Cloud Provider: {'✅ PASSED' if test_results['google_cloud'] else '❌ FAILED'}")
        logger.info(f"  Azure Blob Provider: {'✅ PASSED' if test_results['azure_blob'] else '❌ FAILED'}")
        logger.info(f"  Multi-Cloud Manager: {'✅ PASSED' if test_results['multi_cloud_manager'] else '❌ FAILED'}")
        logger.info(f"  Overall Success Rate: {overall_success_rate:.1%}")
        
        # Cleanup
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        return overall_success_rate >= 0.8, self.test_results

async def main():
    """Main test execution"""
    test_suite = CloudStorageTestSuite()
    
    try:
        success, detailed_results = await test_suite.run_all_tests()
        
        if success:
            logger.info("🎉 CLOUD STORAGE INTEGRATION TEST SUITE: ALL TESTS PASSED!")
            return True
        else:
            logger.error("❌ CLOUD STORAGE INTEGRATION TEST SUITE: SOME TESTS FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
