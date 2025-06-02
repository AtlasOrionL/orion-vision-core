"""
📱 Orion Vision Core - Mobile Integration Module
Cross-platform mobile application framework

This module provides comprehensive mobile capabilities:
- Cross-platform mobile app architecture
- Mobile-specific AI optimizations
- Touch-optimized user interface
- Offline capabilities and local storage
- Mobile performance optimization
- Platform-specific adaptations

Sprint 9.2: Mobile Integration and Cross-Platform
"""

__version__ = "9.2.0"
__author__ = "Orion Vision Core Team"
__status__ = "Development"

# Import core mobile components
try:
    from .mobile_app_foundation import MobileAppFoundation, MobileConfig, PlatformType, AppState, DeviceCapability, DeviceInfo
    from .cross_platform_manager import CrossPlatformManager, PlatformAdapter, AdaptationStrategy, PerformanceProfile
    from .mobile_ui_framework import MobileUIFramework, UIComponent, TouchHandler, ComponentType, GestureType, ThemeMode
    from .offline_manager import OfflineManager, OfflineConfig, SyncStrategy, ConflictResolution, DataPriority
    from .mobile_security import MobileSecurity, BiometricAuth, SecureStorage, BiometricType, SecurityLevel
except ImportError as e:
    # Fallback imports for development
    MobileAppFoundation = None
    CrossPlatformManager = None
    MobileUIFramework = None
    OfflineManager = None
    MobileSecurity = None
    MobileConfig = None
    PlatformType = None
    AppState = None
    DeviceCapability = None
    DeviceInfo = None
    PlatformAdapter = None
    AdaptationStrategy = None
    PerformanceProfile = None
    UIComponent = None
    TouchHandler = None
    ComponentType = None
    GestureType = None
    ThemeMode = None
    OfflineConfig = None
    SyncStrategy = None
    ConflictResolution = None
    DataPriority = None
    BiometricAuth = None
    SecureStorage = None
    BiometricType = None
    SecurityLevel = None

# Module information
def get_module_info():
    """
    Get mobile integration module information and capabilities.

    Returns:
        Dictionary containing mobile module information
    """
    return {
        'module': 'orion_vision_core.mobile',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'MobileAppFoundation': 'Core mobile application architecture',
            'CrossPlatformManager': 'Cross-platform compatibility management',
            'MobileUIFramework': 'Touch-optimized user interface framework',
            'OfflineManager': 'Offline capabilities and data synchronization',
            'MobileSecurity': 'Mobile security and privacy protection'
        },
        'features': [
            'Cross-platform mobile apps (iOS/Android)',
            'Touch-optimized user interface',
            'Offline AI capabilities',
            'Mobile-specific optimizations',
            'Biometric authentication',
            'Secure local storage',
            'Push notifications',
            'Camera and media integration',
            'Mobile gesture recognition',
            'Performance optimization'
        ],
        'supported_platforms': [
            'iOS (iPhone/iPad)',
            'Android (Phone/Tablet)',
            'Windows Mobile',
            'Progressive Web App (PWA)',
            'React Native',
            'Flutter',
            'Xamarin',
            'Cordova/PhoneGap'
        ],
        'ui_frameworks': [
            'Native iOS (Swift/SwiftUI)',
            'Native Android (Kotlin/Jetpack Compose)',
            'React Native',
            'Flutter',
            'Xamarin.Forms',
            'Progressive Web App'
        ],
        'capabilities': {
            'cross_platform': True,
            'offline_support': True,
            'touch_interface': True,
            'biometric_auth': True,
            'push_notifications': True,
            'camera_integration': True,
            'local_ai_processing': True,
            'secure_storage': True
        }
    }

# Export main classes
__all__ = [
    'MobileAppFoundation',
    'CrossPlatformManager',
    'MobileUIFramework',
    'OfflineManager',
    'MobileSecurity',
    'MobileConfig',
    'PlatformType',
    'AppState',
    'DeviceCapability',
    'DeviceInfo',
    'PlatformAdapter',
    'AdaptationStrategy',
    'PerformanceProfile',
    'UIComponent',
    'TouchHandler',
    'ComponentType',
    'GestureType',
    'ThemeMode',
    'OfflineConfig',
    'SyncStrategy',
    'ConflictResolution',
    'DataPriority',
    'BiometricAuth',
    'SecureStorage',
    'BiometricType',
    'SecurityLevel',
    'get_module_info'
]
