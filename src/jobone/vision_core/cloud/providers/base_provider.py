"""
☁️ Orion Vision Core - Base Cloud Provider
Abstract base class for cloud storage providers

This module provides the base interface for all cloud storage providers:
- Common cloud operations interface
- Standardized file and metadata structures
- Error handling and retry mechanisms
- Performance monitoring and metrics

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, BinaryIO
from datetime import datetime
import hashlib
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudOperationType(Enum):
    """Types of cloud operations"""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    DELETE = "delete"
    LIST = "list"
    COPY = "copy"
    MOVE = "move"
    SYNC = "sync"

class CloudFileType(Enum):
    """Types of cloud files"""
    AI_MODEL = "ai_model"
    DATASET = "dataset"
    CONFIG = "config"
    LOG = "log"
    BACKUP = "backup"
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    OTHER = "other"

@dataclass
class CloudMetadata:
    """Metadata for cloud files"""
    file_id: str
    file_name: str
    file_type: CloudFileType
    size_bytes: int
    content_type: str
    created_at: datetime
    modified_at: datetime
    etag: Optional[str] = None
    version: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CloudFile:
    """Cloud file representation"""
    metadata: CloudMetadata
    content: Optional[bytes] = None
    local_path: Optional[str] = None
    cloud_path: str = ""
    provider: str = ""
    bucket_name: str = ""

@dataclass
class CloudOperationResult:
    """Result of a cloud operation"""
    operation: CloudOperationType
    success: bool
    file_path: str
    provider: str
    duration_seconds: float
    bytes_transferred: int = 0
    error_message: Optional[str] = None
    metadata: Optional[CloudMetadata] = None

class BaseCloudProvider(ABC):
    """
    Abstract base class for cloud storage providers.
    
    All cloud providers must implement this interface to ensure
    consistent behavior across different cloud platforms.
    """
    
    def __init__(self, provider_name: str, config: Dict[str, Any]):
        """Initialize the cloud provider"""
        self.provider_name = provider_name
        self.config = config
        self.is_connected = False
        self.operation_history: List[CloudOperationResult] = []
        self.performance_metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'total_bytes_transferred': 0,
            'average_operation_time': 0.0,
            'error_count': 0
        }
        
        logger.info(f"☁️ Initialized {provider_name} cloud provider")
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the cloud provider.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the cloud provider"""
        pass
    
    @abstractmethod
    async def upload_file(self, local_path: str, cloud_path: str, 
                         bucket_name: str, metadata: Optional[Dict[str, Any]] = None) -> CloudOperationResult:
        """
        Upload a file to cloud storage.
        
        Args:
            local_path: Local file path
            cloud_path: Cloud storage path
            bucket_name: Storage bucket/container name
            metadata: Optional file metadata
            
        Returns:
            CloudOperationResult with operation details
        """
        pass
    
    @abstractmethod
    async def download_file(self, cloud_path: str, local_path: str, 
                           bucket_name: str) -> CloudOperationResult:
        """
        Download a file from cloud storage.
        
        Args:
            cloud_path: Cloud storage path
            local_path: Local destination path
            bucket_name: Storage bucket/container name
            
        Returns:
            CloudOperationResult with operation details
        """
        pass
    
    @abstractmethod
    async def delete_file(self, cloud_path: str, bucket_name: str) -> CloudOperationResult:
        """
        Delete a file from cloud storage.
        
        Args:
            cloud_path: Cloud storage path
            bucket_name: Storage bucket/container name
            
        Returns:
            CloudOperationResult with operation details
        """
        pass
    
    @abstractmethod
    async def list_files(self, bucket_name: str, prefix: str = "", 
                        max_results: int = 1000) -> List[CloudMetadata]:
        """
        List files in cloud storage.
        
        Args:
            bucket_name: Storage bucket/container name
            prefix: File path prefix filter
            max_results: Maximum number of results
            
        Returns:
            List of CloudMetadata objects
        """
        pass
    
    @abstractmethod
    async def file_exists(self, cloud_path: str, bucket_name: str) -> bool:
        """
        Check if a file exists in cloud storage.
        
        Args:
            cloud_path: Cloud storage path
            bucket_name: Storage bucket/container name
            
        Returns:
            True if file exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_file_metadata(self, cloud_path: str, bucket_name: str) -> Optional[CloudMetadata]:
        """
        Get metadata for a file in cloud storage.
        
        Args:
            cloud_path: Cloud storage path
            bucket_name: Storage bucket/container name
            
        Returns:
            CloudMetadata object or None if file doesn't exist
        """
        pass
    
    async def copy_file(self, source_path: str, dest_path: str, 
                       bucket_name: str) -> CloudOperationResult:
        """
        Copy a file within cloud storage.
        
        Args:
            source_path: Source cloud path
            dest_path: Destination cloud path
            bucket_name: Storage bucket/container name
            
        Returns:
            CloudOperationResult with operation details
        """
        # Default implementation using download/upload
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Download to temporary location
            temp_path = f"/tmp/{hashlib.md5(source_path.encode()).hexdigest()}"
            
            download_result = await self.download_file(source_path, temp_path, bucket_name)
            if not download_result.success:
                return CloudOperationResult(
                    operation=CloudOperationType.COPY,
                    success=False,
                    file_path=source_path,
                    provider=self.provider_name,
                    duration_seconds=asyncio.get_event_loop().time() - start_time,
                    error_message=f"Failed to download source file: {download_result.error_message}"
                )
            
            # Upload to destination
            upload_result = await self.upload_file(temp_path, dest_path, bucket_name)
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            duration = asyncio.get_event_loop().time() - start_time
            
            result = CloudOperationResult(
                operation=CloudOperationType.COPY,
                success=upload_result.success,
                file_path=f"{source_path} -> {dest_path}",
                provider=self.provider_name,
                duration_seconds=duration,
                bytes_transferred=upload_result.bytes_transferred,
                error_message=upload_result.error_message
            )
            
            self._record_operation(result)
            return result
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            result = CloudOperationResult(
                operation=CloudOperationType.COPY,
                success=False,
                file_path=source_path,
                provider=self.provider_name,
                duration_seconds=duration,
                error_message=str(e)
            )
            self._record_operation(result)
            return result
    
    def _record_operation(self, result: CloudOperationResult):
        """Record operation for metrics and history"""
        self.operation_history.append(result)
        
        # Update metrics
        self.performance_metrics['total_operations'] += 1
        
        if result.success:
            self.performance_metrics['successful_operations'] += 1
            self.performance_metrics['total_bytes_transferred'] += result.bytes_transferred
        else:
            self.performance_metrics['error_count'] += 1
        
        # Update average operation time
        total_ops = self.performance_metrics['total_operations']
        current_avg = self.performance_metrics['average_operation_time']
        self.performance_metrics['average_operation_time'] = (
            (current_avg * (total_ops - 1) + result.duration_seconds) / total_ops
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this provider"""
        total_ops = self.performance_metrics['total_operations']
        success_rate = (
            self.performance_metrics['successful_operations'] / total_ops 
            if total_ops > 0 else 0.0
        )
        
        return {
            **self.performance_metrics,
            'success_rate': success_rate,
            'provider_name': self.provider_name,
            'is_connected': self.is_connected
        }
    
    def get_recent_operations(self, limit: int = 10) -> List[CloudOperationResult]:
        """Get recent operations history"""
        return self.operation_history[-limit:] if self.operation_history else []
