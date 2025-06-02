"""
☁️ Orion Vision Core - Cloud Storage Manager
Unified multi-cloud storage management

This module provides unified cloud storage management:
- Multi-cloud provider support (AWS S3, Google Cloud, Azure Blob)
- Unified storage interface across providers
- Automatic provider selection and load balancing
- Cross-cloud data migration and synchronization
- Storage cost optimization and monitoring

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import os

from .providers.base_provider import BaseCloudProvider, CloudFile, CloudMetadata, CloudOperationResult
from .providers.aws_s3 import AWSS3Provider
from .providers.google_cloud import GoogleCloudProvider
from .providers.azure_blob import AzureBlobProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageProvider(Enum):
    """Supported cloud storage providers"""
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    LOCAL = "local"

class StorageStrategy(Enum):
    """Storage strategies for multi-cloud operations"""
    PRIMARY_ONLY = "primary_only"
    REDUNDANT = "redundant"
    LOAD_BALANCED = "load_balanced"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"

@dataclass
class StorageConfig:
    """Configuration for cloud storage"""
    primary_provider: StorageProvider
    backup_providers: List[StorageProvider] = field(default_factory=list)
    strategy: StorageStrategy = StorageStrategy.PRIMARY_ONLY
    auto_sync: bool = True
    encryption_enabled: bool = True
    compression_enabled: bool = False
    retry_attempts: int = 3
    timeout_seconds: float = 30.0

@dataclass
class StorageMetrics:
    """Storage performance and cost metrics"""
    total_files: int = 0
    total_size_bytes: int = 0
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_cost: float = 0.0
    average_operation_time: float = 0.0
    provider_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)

class CloudStorageManager:
    """
    Unified cloud storage manager for Orion Vision Core.
    
    Manages multiple cloud storage providers with:
    - Unified interface across all providers
    - Automatic provider selection and failover
    - Cross-cloud data migration
    - Cost and performance optimization
    - Storage monitoring and analytics
    """
    
    def __init__(self, config: StorageConfig, provider_configs: Dict[str, Dict[str, Any]]):
        """
        Initialize cloud storage manager.
        
        Args:
            config: Storage configuration
            provider_configs: Configuration for each provider
        """
        self.config = config
        self.provider_configs = provider_configs
        self.providers: Dict[StorageProvider, BaseCloudProvider] = {}
        self.metrics = StorageMetrics()
        self.operation_history: List[CloudOperationResult] = []
        
        # Initialize providers
        self._initialize_providers()
        
        logger.info("☁️ Cloud Storage Manager initialized")
    
    def _initialize_providers(self):
        """Initialize cloud storage providers"""
        
        # Initialize primary provider
        if self.config.primary_provider in self.provider_configs:
            provider = self._create_provider(
                self.config.primary_provider,
                self.provider_configs[self.config.primary_provider]
            )
            if provider:
                self.providers[self.config.primary_provider] = provider
        
        # Initialize backup providers
        for backup_provider in self.config.backup_providers:
            if backup_provider in self.provider_configs:
                provider = self._create_provider(
                    backup_provider,
                    self.provider_configs[backup_provider]
                )
                if provider:
                    self.providers[backup_provider] = provider
        
        logger.info(f"📋 Initialized {len(self.providers)} cloud storage providers")
    
    def _create_provider(self, provider_type: StorageProvider, config: Dict[str, Any]) -> Optional[BaseCloudProvider]:
        """Create a cloud storage provider instance"""
        
        try:
            if provider_type == StorageProvider.AWS_S3:
                return AWSS3Provider(config)
            elif provider_type == StorageProvider.GOOGLE_CLOUD:
                return GoogleCloudProvider(config)
            elif provider_type == StorageProvider.AZURE_BLOB:
                return AzureBlobProvider(config)
            else:
                logger.warning(f"⚠️ Unsupported provider type: {provider_type}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to create provider {provider_type}: {e}")
            return None
    
    async def connect_all_providers(self) -> Dict[StorageProvider, bool]:
        """Connect to all configured providers"""
        
        connection_results = {}
        
        for provider_type, provider in self.providers.items():
            try:
                success = await provider.connect()
                connection_results[provider_type] = success
                
                if success:
                    logger.info(f"✅ Connected to {provider_type.value}")
                else:
                    logger.error(f"❌ Failed to connect to {provider_type.value}")
                    
            except Exception as e:
                logger.error(f"❌ Connection error for {provider_type.value}: {e}")
                connection_results[provider_type] = False
        
        return connection_results
    
    async def disconnect_all_providers(self):
        """Disconnect from all providers"""
        
        for provider_type, provider in self.providers.items():
            try:
                await provider.disconnect()
                logger.info(f"🔌 Disconnected from {provider_type.value}")
            except Exception as e:
                logger.error(f"❌ Disconnect error for {provider_type.value}: {e}")
    
    async def upload_file(self, local_path: str, cloud_path: str, bucket_name: str,
                         metadata: Optional[Dict[str, Any]] = None,
                         provider: Optional[StorageProvider] = None) -> CloudOperationResult:
        """
        Upload file to cloud storage.
        
        Args:
            local_path: Local file path
            cloud_path: Cloud storage path
            bucket_name: Storage bucket/container name
            metadata: Optional file metadata
            provider: Specific provider to use (optional)
            
        Returns:
            CloudOperationResult with operation details
        """
        
        target_provider = provider or self.config.primary_provider
        
        if target_provider not in self.providers:
            return CloudOperationResult(
                operation="upload",
                success=False,
                file_path=cloud_path,
                provider="none",
                duration_seconds=0.0,
                error_message=f"Provider {target_provider} not available"
            )
        
        # Upload to primary provider
        result = await self.providers[target_provider].upload_file(
            local_path, cloud_path, bucket_name, metadata
        )
        
        self._record_operation(result)
        
        # Handle redundant storage if configured
        if (self.config.strategy == StorageStrategy.REDUNDANT and 
            result.success and self.config.backup_providers):
            
            await self._replicate_to_backup_providers(
                local_path, cloud_path, bucket_name, metadata
            )
        
        return result
    
    async def download_file(self, cloud_path: str, local_path: str, bucket_name: str,
                           provider: Optional[StorageProvider] = None) -> CloudOperationResult:
        """
        Download file from cloud storage.
        
        Args:
            cloud_path: Cloud storage path
            local_path: Local destination path
            bucket_name: Storage bucket/container name
            provider: Specific provider to use (optional)
            
        Returns:
            CloudOperationResult with operation details
        """
        
        target_provider = provider or self.config.primary_provider
        
        if target_provider not in self.providers:
            return CloudOperationResult(
                operation="download",
                success=False,
                file_path=cloud_path,
                provider="none",
                duration_seconds=0.0,
                error_message=f"Provider {target_provider} not available"
            )
        
        # Try primary provider first
        result = await self.providers[target_provider].download_file(
            cloud_path, local_path, bucket_name
        )
        
        # If primary fails, try backup providers
        if not result.success and self.config.backup_providers:
            for backup_provider in self.config.backup_providers:
                if backup_provider in self.providers:
                    logger.info(f"🔄 Trying backup provider: {backup_provider.value}")
                    
                    backup_result = await self.providers[backup_provider].download_file(
                        cloud_path, local_path, bucket_name
                    )
                    
                    if backup_result.success:
                        result = backup_result
                        break
        
        self._record_operation(result)
        return result
    
    async def delete_file(self, cloud_path: str, bucket_name: str,
                         provider: Optional[StorageProvider] = None,
                         delete_from_all: bool = False) -> Dict[StorageProvider, CloudOperationResult]:
        """
        Delete file from cloud storage.
        
        Args:
            cloud_path: Cloud storage path
            bucket_name: Storage bucket/container name
            provider: Specific provider to use (optional)
            delete_from_all: Whether to delete from all providers
            
        Returns:
            Dictionary of results per provider
        """
        
        results = {}
        
        if delete_from_all:
            # Delete from all providers
            for provider_type, provider_instance in self.providers.items():
                result = await provider_instance.delete_file(cloud_path, bucket_name)
                results[provider_type] = result
                self._record_operation(result)
        else:
            # Delete from specific or primary provider
            target_provider = provider or self.config.primary_provider
            
            if target_provider in self.providers:
                result = await self.providers[target_provider].delete_file(
                    cloud_path, bucket_name
                )
                results[target_provider] = result
                self._record_operation(result)
        
        return results
    
    async def list_files(self, bucket_name: str, prefix: str = "",
                        max_results: int = 1000,
                        provider: Optional[StorageProvider] = None) -> List[CloudMetadata]:
        """
        List files in cloud storage.
        
        Args:
            bucket_name: Storage bucket/container name
            prefix: File path prefix filter
            max_results: Maximum number of results
            provider: Specific provider to use (optional)
            
        Returns:
            List of CloudMetadata objects
        """
        
        target_provider = provider or self.config.primary_provider
        
        if target_provider not in self.providers:
            logger.error(f"❌ Provider {target_provider} not available")
            return []
        
        try:
            files = await self.providers[target_provider].list_files(
                bucket_name, prefix, max_results
            )
            
            logger.info(f"📋 Listed {len(files)} files from {target_provider.value}")
            return files
            
        except Exception as e:
            logger.error(f"❌ Failed to list files: {e}")
            return []
    
    async def file_exists(self, cloud_path: str, bucket_name: str,
                         provider: Optional[StorageProvider] = None) -> bool:
        """
        Check if file exists in cloud storage.
        
        Args:
            cloud_path: Cloud storage path
            bucket_name: Storage bucket/container name
            provider: Specific provider to use (optional)
            
        Returns:
            True if file exists, False otherwise
        """
        
        target_provider = provider or self.config.primary_provider
        
        if target_provider not in self.providers:
            return False
        
        try:
            exists = await self.providers[target_provider].file_exists(
                cloud_path, bucket_name
            )
            return exists
            
        except Exception as e:
            logger.error(f"❌ Failed to check file existence: {e}")
            return False
    
    async def _replicate_to_backup_providers(self, local_path: str, cloud_path: str,
                                           bucket_name: str, metadata: Optional[Dict[str, Any]]):
        """Replicate file to backup providers for redundancy"""
        
        for backup_provider in self.config.backup_providers:
            if backup_provider in self.providers:
                try:
                    logger.info(f"🔄 Replicating to backup provider: {backup_provider.value}")
                    
                    result = await self.providers[backup_provider].upload_file(
                        local_path, cloud_path, bucket_name, metadata
                    )
                    
                    if result.success:
                        logger.info(f"✅ Successfully replicated to {backup_provider.value}")
                    else:
                        logger.warning(f"⚠️ Failed to replicate to {backup_provider.value}: {result.error_message}")
                        
                except Exception as e:
                    logger.error(f"❌ Replication error for {backup_provider.value}: {e}")
    
    def _record_operation(self, result: CloudOperationResult):
        """Record operation for metrics and history"""
        
        self.operation_history.append(result)
        
        # Update global metrics
        self.metrics.total_operations += 1
        
        if result.success:
            self.metrics.successful_operations += 1
        else:
            self.metrics.failed_operations += 1
        
        # Update average operation time
        total_ops = self.metrics.total_operations
        current_avg = self.metrics.average_operation_time
        self.metrics.average_operation_time = (
            (current_avg * (total_ops - 1) + result.duration_seconds) / total_ops
        )
        
        # Update provider-specific metrics
        provider_name = result.provider
        if provider_name not in self.metrics.provider_metrics:
            self.metrics.provider_metrics[provider_name] = {
                'operations': 0,
                'successful': 0,
                'failed': 0,
                'bytes_transferred': 0
            }
        
        provider_metrics = self.metrics.provider_metrics[provider_name]
        provider_metrics['operations'] += 1
        
        if result.success:
            provider_metrics['successful'] += 1
            provider_metrics['bytes_transferred'] += result.bytes_transferred
        else:
            provider_metrics['failed'] += 1
    
    def get_storage_metrics(self) -> StorageMetrics:
        """Get comprehensive storage metrics"""
        return self.metrics
    
    def get_provider_status(self) -> Dict[StorageProvider, Dict[str, Any]]:
        """Get status of all providers"""
        
        status = {}
        
        for provider_type, provider in self.providers.items():
            status[provider_type] = {
                'connected': provider.is_connected,
                'performance_metrics': provider.get_performance_metrics(),
                'recent_operations': len(provider.get_recent_operations())
            }
        
        return status
    
    def get_recent_operations(self, limit: int = 10) -> List[CloudOperationResult]:
        """Get recent operations across all providers"""
        return self.operation_history[-limit:] if self.operation_history else []
