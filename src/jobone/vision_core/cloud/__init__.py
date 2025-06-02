"""
☁️ Orion Vision Core - Cloud Integration Module
Multi-cloud storage and synchronization capabilities

This module provides comprehensive cloud integration:
- Multi-cloud storage support (AWS S3, Google Cloud, Azure Blob)
- Unified cloud storage interface
- Automatic synchronization and backup
- Cloud-based AI model storage and retrieval
- Secure credential management
- Cross-cloud data migration

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

__version__ = "9.1.0"
__author__ = "Orion Vision Core Team"
__status__ = "Development"

# Import core cloud components
try:
    from .storage_manager import CloudStorageManager, StorageProvider, StorageConfig
    from .sync_manager import CloudSyncManager, SyncStrategy, SyncConfig
    from .providers.aws_s3 import AWSS3Provider
    from .providers.google_cloud import GoogleCloudProvider
    from .providers.azure_blob import AzureBlobProvider
    from .providers.base_provider import BaseCloudProvider, CloudFile, CloudMetadata
except ImportError as e:
    # Fallback imports for development
    CloudStorageManager = None
    CloudSyncManager = None
    StorageProvider = None
    StorageConfig = None
    SyncStrategy = None
    SyncConfig = None
    AWSS3Provider = None
    GoogleCloudProvider = None
    AzureBlobProvider = None
    BaseCloudProvider = None
    CloudFile = None
    CloudMetadata = None

# Module information
def get_module_info():
    """
    Get cloud module information and capabilities.
    
    Returns:
        Dictionary containing cloud module information
    """
    return {
        'module': 'orion_vision_core.cloud',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'CloudStorageManager': 'Multi-cloud storage management',
            'CloudSyncManager': 'Cloud synchronization and backup',
            'AWSS3Provider': 'Amazon S3 storage provider',
            'GoogleCloudProvider': 'Google Cloud Storage provider',
            'AzureBlobProvider': 'Azure Blob Storage provider'
        },
        'features': [
            'Multi-cloud storage support',
            'Unified storage interface',
            'Automatic synchronization',
            'Secure credential management',
            'Cross-cloud migration',
            'AI model cloud storage',
            'Backup and recovery',
            'Performance optimization'
        ],
        'supported_providers': [
            'AWS S3',
            'Google Cloud Storage',
            'Azure Blob Storage',
            'Local filesystem (fallback)',
            'Custom providers'
        ],
        'capabilities': {
            'multi_cloud_support': True,
            'automatic_sync': True,
            'secure_storage': True,
            'cross_cloud_migration': True,
            'ai_model_storage': True,
            'backup_recovery': True,
            'performance_optimization': True,
            'custom_providers': True
        }
    }

# Export main classes
__all__ = [
    'CloudStorageManager',
    'CloudSyncManager',
    'StorageProvider',
    'StorageConfig',
    'SyncStrategy',
    'SyncConfig',
    'AWSS3Provider',
    'GoogleCloudProvider',
    'AzureBlobProvider',
    'BaseCloudProvider',
    'CloudFile',
    'CloudMetadata',
    'get_module_info'
]
