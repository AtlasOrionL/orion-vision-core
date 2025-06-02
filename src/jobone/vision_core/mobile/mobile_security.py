"""
🔐 Orion Vision Core - Mobile Security
Mobile security and privacy protection

This module provides mobile security capabilities:
- Biometric authentication integration
- Secure local data storage
- Privacy-first design principles
- Mobile security protocols
- Data encryption and protection

Sprint 9.2: Mobile Integration and Cross-Platform
"""

import asyncio
import logging
import hashlib
import secrets
import base64
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import json
import os

from .mobile_app_foundation import DeviceCapability

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BiometricType(Enum):
    """Biometric authentication types"""
    FINGERPRINT = "fingerprint"
    FACE_ID = "face_id"
    VOICE = "voice"
    IRIS = "iris"
    PALM = "palm"

class SecurityLevel(Enum):
    """Security levels"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"

class EncryptionAlgorithm(Enum):
    """Encryption algorithms"""
    AES_256 = "aes_256"
    CHACHA20 = "chacha20"
    RSA_2048 = "rsa_2048"
    ECDSA = "ecdsa"

class AuthenticationResult(Enum):
    """Authentication result types"""
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    NOT_AVAILABLE = "not_available"
    NOT_ENROLLED = "not_enrolled"
    LOCKED_OUT = "locked_out"

@dataclass
class BiometricConfig:
    """Biometric authentication configuration"""
    enabled: bool = True
    allowed_types: List[BiometricType] = field(default_factory=lambda: [BiometricType.FINGERPRINT, BiometricType.FACE_ID])
    fallback_to_passcode: bool = True
    max_attempts: int = 3
    lockout_duration_minutes: int = 5
    require_confirmation: bool = True

@dataclass
class SecurityConfig:
    """Security configuration"""
    security_level: SecurityLevel = SecurityLevel.STANDARD
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256
    biometric_config: BiometricConfig = field(default_factory=BiometricConfig)
    auto_lock_enabled: bool = True
    auto_lock_timeout_minutes: int = 5
    secure_storage_enabled: bool = True
    network_security_enabled: bool = True
    app_integrity_check: bool = True
    debug_protection: bool = True

@dataclass
class AuthenticationAttempt:
    """Authentication attempt record"""
    attempt_id: str
    biometric_type: BiometricType
    result: AuthenticationResult
    timestamp: datetime = field(default_factory=datetime.now)
    device_info: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass
class SecureStorageItem:
    """Secure storage item"""
    key: str
    encrypted_value: str
    algorithm: EncryptionAlgorithm
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0

class BiometricAuth:
    """
    Biometric authentication manager.
    
    Provides biometric authentication capabilities with:
    - Multiple biometric type support
    - Fallback authentication methods
    - Security attempt tracking
    - Lockout protection
    """
    
    def __init__(self, config: Optional[BiometricConfig] = None):
        """
        Initialize biometric authentication.
        
        Args:
            config: Biometric configuration
        """
        self.config = config or BiometricConfig()
        self.available_types: List[BiometricType] = []
        self.authentication_attempts: List[AuthenticationAttempt] = []
        self.is_locked_out = False
        self.lockout_until: Optional[datetime] = None
        
        # Performance metrics
        self.metrics = {
            'total_attempts': 0,
            'successful_attempts': 0,
            'failed_attempts': 0,
            'lockout_events': 0,
            'average_auth_time': 0.0
        }
        
        logger.info("🔐 Biometric Authentication initialized")
    
    async def initialize(self, available_capabilities: List[DeviceCapability]) -> bool:
        """
        Initialize biometric authentication with device capabilities.
        
        Args:
            available_capabilities: Available device capabilities
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Check for biometric capability
            if DeviceCapability.BIOMETRIC not in available_capabilities:
                logger.warning("⚠️ Biometric capability not available on device")
                return False
            
            # Detect available biometric types
            self.available_types = await self._detect_available_biometrics()
            
            if not self.available_types:
                logger.warning("⚠️ No biometric types available")
                return False
            
            logger.info(f"✅ Biometric authentication initialized with {len(self.available_types)} types")
            return True
            
        except Exception as e:
            logger.error(f"❌ Biometric authentication initialization failed: {e}")
            return False
    
    async def _detect_available_biometrics(self) -> List[BiometricType]:
        """Detect available biometric types on device"""
        
        # Simulate biometric detection (in real implementation, use platform APIs)
        available = []
        
        # Most modern devices support fingerprint
        available.append(BiometricType.FINGERPRINT)
        
        # Many newer devices support face recognition
        available.append(BiometricType.FACE_ID)
        
        # Filter by allowed types
        return [bt for bt in available if bt in self.config.allowed_types]
    
    async def authenticate(self, biometric_type: Optional[BiometricType] = None,
                          prompt: str = "Authenticate to continue") -> AuthenticationResult:
        """
        Perform biometric authentication.
        
        Args:
            biometric_type: Specific biometric type (auto-select if None)
            prompt: Authentication prompt message
            
        Returns:
            AuthenticationResult
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Check if locked out
            if await self._is_locked_out():
                return AuthenticationResult.LOCKED_OUT
            
            # Select biometric type
            if biometric_type is None:
                if not self.available_types:
                    return AuthenticationResult.NOT_AVAILABLE
                biometric_type = self.available_types[0]  # Use first available
            
            if biometric_type not in self.available_types:
                return AuthenticationResult.NOT_AVAILABLE
            
            # Perform authentication
            result = await self._perform_biometric_auth(biometric_type, prompt)
            
            # Record attempt
            attempt = AuthenticationAttempt(
                attempt_id=secrets.token_hex(8),
                biometric_type=biometric_type,
                result=result
            )
            self.authentication_attempts.append(attempt)
            
            # Update metrics
            auth_time = asyncio.get_event_loop().time() - start_time
            self._update_auth_metrics(result, auth_time)
            
            # Handle failed attempts
            if result == AuthenticationResult.FAILURE:
                await self._handle_failed_attempt()
            
            logger.info(f"🔐 Biometric auth result: {result.value} ({biometric_type.value})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Biometric authentication error: {e}")
            return AuthenticationResult.FAILURE
    
    async def _perform_biometric_auth(self, biometric_type: BiometricType, prompt: str) -> AuthenticationResult:
        """Perform the actual biometric authentication"""
        
        # Simulate biometric authentication (in real implementation, use platform APIs)
        await asyncio.sleep(0.5)  # Simulate auth time
        
        # Simulate success/failure (90% success rate for demo)
        import random
        if random.random() < 0.9:
            return AuthenticationResult.SUCCESS
        else:
            return AuthenticationResult.FAILURE
    
    async def _is_locked_out(self) -> bool:
        """Check if authentication is locked out"""
        
        if not self.is_locked_out:
            return False
        
        if self.lockout_until and datetime.now() >= self.lockout_until:
            # Lockout period expired
            self.is_locked_out = False
            self.lockout_until = None
            logger.info("🔓 Biometric lockout expired")
            return False
        
        return True
    
    async def _handle_failed_attempt(self):
        """Handle failed authentication attempt"""
        
        # Count recent failed attempts
        recent_failures = [
            attempt for attempt in self.authentication_attempts[-self.config.max_attempts:]
            if attempt.result == AuthenticationResult.FAILURE
        ]
        
        if len(recent_failures) >= self.config.max_attempts:
            # Lock out authentication
            self.is_locked_out = True
            self.lockout_until = datetime.now() + timedelta(minutes=self.config.lockout_duration_minutes)
            self.metrics['lockout_events'] += 1
            
            logger.warning(f"🔒 Biometric authentication locked out for {self.config.lockout_duration_minutes} minutes")
    
    def _update_auth_metrics(self, result: AuthenticationResult, auth_time: float):
        """Update authentication metrics"""
        
        self.metrics['total_attempts'] += 1
        
        if result == AuthenticationResult.SUCCESS:
            self.metrics['successful_attempts'] += 1
        else:
            self.metrics['failed_attempts'] += 1
        
        # Update average auth time
        total_attempts = self.metrics['total_attempts']
        current_avg = self.metrics['average_auth_time']
        self.metrics['average_auth_time'] = (
            (current_avg * (total_attempts - 1) + auth_time) / total_attempts
        )
    
    def get_auth_metrics(self) -> Dict[str, Any]:
        """Get authentication metrics"""
        
        success_rate = 0.0
        if self.metrics['total_attempts'] > 0:
            success_rate = self.metrics['successful_attempts'] / self.metrics['total_attempts']
        
        return {
            **self.metrics,
            'success_rate': success_rate,
            'available_types': [bt.value for bt in self.available_types],
            'is_locked_out': self.is_locked_out,
            'lockout_until': self.lockout_until.isoformat() if self.lockout_until else None
        }

class SecureStorage:
    """
    Secure local data storage manager.
    
    Provides secure storage capabilities with:
    - Data encryption and decryption
    - Secure key management
    - Access tracking and auditing
    - Multiple encryption algorithms
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """
        Initialize secure storage.
        
        Args:
            config: Security configuration
        """
        self.config = config or SecurityConfig()
        self.storage_path = "./secure_storage"
        self.master_key: Optional[bytes] = None
        self.storage_items: Dict[str, SecureStorageItem] = {}
        
        # Performance metrics
        self.metrics = {
            'items_stored': 0,
            'items_retrieved': 0,
            'encryption_operations': 0,
            'decryption_operations': 0,
            'average_encryption_time': 0.0
        }
        
        logger.info("🔐 Secure Storage initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize secure storage.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create storage directory
            os.makedirs(self.storage_path, exist_ok=True)
            
            # Generate or load master key
            await self._initialize_master_key()
            
            # Load existing items
            await self._load_storage_items()
            
            logger.info(f"✅ Secure storage initialized with {len(self.storage_items)} items")
            return True
            
        except Exception as e:
            logger.error(f"❌ Secure storage initialization failed: {e}")
            return False
    
    async def _initialize_master_key(self):
        """Initialize master encryption key"""
        
        key_file = os.path.join(self.storage_path, "master.key")
        
        if os.path.exists(key_file):
            # Load existing key
            with open(key_file, 'rb') as f:
                self.master_key = f.read()
        else:
            # Generate new key
            self.master_key = secrets.token_bytes(32)  # 256-bit key
            
            # Save key securely
            with open(key_file, 'wb') as f:
                f.write(self.master_key)
            
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
        
        logger.info("🔑 Master key initialized")
    
    async def _load_storage_items(self):
        """Load storage items from disk"""
        
        items_file = os.path.join(self.storage_path, "items.json")
        
        if os.path.exists(items_file):
            try:
                with open(items_file, 'r') as f:
                    items_data = json.load(f)
                
                for key, item_data in items_data.items():
                    item = SecureStorageItem(
                        key=item_data['key'],
                        encrypted_value=item_data['encrypted_value'],
                        algorithm=EncryptionAlgorithm(item_data['algorithm']),
                        created_at=datetime.fromisoformat(item_data['created_at']),
                        accessed_at=datetime.fromisoformat(item_data['accessed_at']),
                        access_count=item_data['access_count']
                    )
                    self.storage_items[key] = item
                
            except Exception as e:
                logger.error(f"❌ Failed to load storage items: {e}")
    
    async def _save_storage_items(self):
        """Save storage items to disk"""
        
        items_file = os.path.join(self.storage_path, "items.json")
        
        try:
            items_data = {}
            for key, item in self.storage_items.items():
                items_data[key] = {
                    'key': item.key,
                    'encrypted_value': item.encrypted_value,
                    'algorithm': item.algorithm.value,
                    'created_at': item.created_at.isoformat(),
                    'accessed_at': item.accessed_at.isoformat(),
                    'access_count': item.access_count
                }
            
            with open(items_file, 'w') as f:
                json.dump(items_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Failed to save storage items: {e}")
    
    async def store(self, key: str, value: Any) -> bool:
        """
        Store data securely.
        
        Args:
            key: Storage key
            value: Data to store
            
        Returns:
            True if storage successful, False otherwise
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Serialize value
            value_str = json.dumps(value)
            
            # Encrypt value
            encrypted_value = await self._encrypt(value_str)
            
            # Create storage item
            item = SecureStorageItem(
                key=key,
                encrypted_value=encrypted_value,
                algorithm=self.config.encryption_algorithm
            )
            
            # Store item
            self.storage_items[key] = item
            
            # Save to disk
            await self._save_storage_items()
            
            # Update metrics
            encryption_time = asyncio.get_event_loop().time() - start_time
            self._update_encryption_metrics(encryption_time)
            self.metrics['items_stored'] += 1
            
            logger.info(f"🔐 Stored secure data: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store secure data: {e}")
            return False
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data securely.
        
        Args:
            key: Storage key
            
        Returns:
            Decrypted data if found, None otherwise
        """
        try:
            if key not in self.storage_items:
                return None
            
            start_time = asyncio.get_event_loop().time()
            
            item = self.storage_items[key]
            
            # Decrypt value
            decrypted_value = await self._decrypt(item.encrypted_value)
            
            # Deserialize value
            value = json.loads(decrypted_value)
            
            # Update access tracking
            item.accessed_at = datetime.now()
            item.access_count += 1
            
            # Save updated item
            await self._save_storage_items()
            
            # Update metrics
            decryption_time = asyncio.get_event_loop().time() - start_time
            self.metrics['decryption_operations'] += 1
            self.metrics['items_retrieved'] += 1
            
            logger.info(f"🔓 Retrieved secure data: {key}")
            return value
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve secure data: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Delete stored data.
        
        Args:
            key: Storage key
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            if key in self.storage_items:
                del self.storage_items[key]
                await self._save_storage_items()
                logger.info(f"🗑️ Deleted secure data: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete secure data: {e}")
            return False
    
    async def _encrypt(self, data: str) -> str:
        """Encrypt data using configured algorithm"""
        
        if not self.master_key:
            raise ValueError("Master key not initialized")
        
        # Simple encryption simulation (in real implementation, use proper crypto libraries)
        data_bytes = data.encode('utf-8')
        
        # XOR with master key (simplified - use proper AES in production)
        encrypted_bytes = bytes(a ^ b for a, b in zip(data_bytes, self.master_key * (len(data_bytes) // len(self.master_key) + 1)))
        
        # Base64 encode
        encrypted_str = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        self.metrics['encryption_operations'] += 1
        return encrypted_str
    
    async def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt data using configured algorithm"""
        
        if not self.master_key:
            raise ValueError("Master key not initialized")
        
        # Base64 decode
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # XOR with master key (simplified - use proper AES in production)
        decrypted_bytes = bytes(a ^ b for a, b in zip(encrypted_bytes, self.master_key * (len(encrypted_bytes) // len(self.master_key) + 1)))
        
        # Decode to string
        decrypted_str = decrypted_bytes.decode('utf-8')
        
        self.metrics['decryption_operations'] += 1
        return decrypted_str
    
    def _update_encryption_metrics(self, encryption_time: float):
        """Update encryption metrics"""
        
        total_ops = self.metrics['encryption_operations']
        current_avg = self.metrics['average_encryption_time']
        self.metrics['average_encryption_time'] = (
            (current_avg * (total_ops - 1) + encryption_time) / total_ops
        )
    
    def get_storage_metrics(self) -> Dict[str, Any]:
        """Get secure storage metrics"""
        
        return {
            **self.metrics,
            'total_items': len(self.storage_items),
            'storage_path': self.storage_path,
            'encryption_algorithm': self.config.encryption_algorithm.value
        }

class MobileSecurity:
    """
    Mobile security and privacy protection manager.
    
    Provides comprehensive mobile security with:
    - Biometric authentication
    - Secure data storage
    - Privacy protection
    - Security monitoring
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """
        Initialize mobile security.
        
        Args:
            config: Security configuration
        """
        self.config = config or SecurityConfig()
        self.biometric_auth = BiometricAuth(self.config.biometric_config)
        self.secure_storage = SecureStorage(self.config)
        
        # Security state
        self.is_authenticated = False
        self.last_activity_time = datetime.now()
        self.auto_lock_task: Optional[asyncio.Task] = None
        
        # Security event handlers
        self.security_handlers: List[Callable] = []
        
        logger.info("🔐 Mobile Security initialized")
    
    async def initialize(self, available_capabilities: List[DeviceCapability]) -> bool:
        """
        Initialize mobile security.
        
        Args:
            available_capabilities: Available device capabilities
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize biometric authentication
            biometric_success = await self.biometric_auth.initialize(available_capabilities)
            
            # Initialize secure storage
            storage_success = await self.secure_storage.initialize()
            
            # Start auto-lock if enabled
            if self.config.auto_lock_enabled:
                await self._start_auto_lock()
            
            success = biometric_success and storage_success
            
            logger.info(f"✅ Mobile Security initialized: biometric={biometric_success}, storage={storage_success}")
            return success
            
        except Exception as e:
            logger.error(f"❌ Mobile Security initialization failed: {e}")
            return False
    
    async def authenticate(self, biometric_type: Optional[BiometricType] = None) -> bool:
        """
        Authenticate user.
        
        Args:
            biometric_type: Specific biometric type
            
        Returns:
            True if authentication successful, False otherwise
        """
        result = await self.biometric_auth.authenticate(biometric_type)
        
        if result == AuthenticationResult.SUCCESS:
            self.is_authenticated = True
            self.last_activity_time = datetime.now()
            
            # Trigger security handlers
            for handler in self.security_handlers:
                try:
                    await handler("authentication_success")
                except Exception as e:
                    logger.error(f"❌ Security handler error: {e}")
            
            return True
        
        return False
    
    async def _start_auto_lock(self):
        """Start auto-lock monitoring"""
        
        if self.auto_lock_task and not self.auto_lock_task.done():
            return
        
        self.auto_lock_task = asyncio.create_task(self._auto_lock_loop())
        logger.info("🔒 Auto-lock monitoring started")
    
    async def _auto_lock_loop(self):
        """Auto-lock monitoring loop"""
        
        while True:
            try:
                if self.is_authenticated:
                    time_since_activity = datetime.now() - self.last_activity_time
                    timeout = timedelta(minutes=self.config.auto_lock_timeout_minutes)
                    
                    if time_since_activity >= timeout:
                        await self.lock()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Auto-lock error: {e}")
                await asyncio.sleep(60)
    
    async def lock(self):
        """Lock the application"""
        
        self.is_authenticated = False
        
        # Trigger security handlers
        for handler in self.security_handlers:
            try:
                await handler("application_locked")
            except Exception as e:
                logger.error(f"❌ Security handler error: {e}")
        
        logger.info("🔒 Application locked")
    
    def register_security_handler(self, handler: Callable):
        """Register security event handler"""
        self.security_handlers.append(handler)
        logger.info("📡 Registered security handler")
    
    def update_activity(self):
        """Update last activity time"""
        self.last_activity_time = datetime.now()
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security status"""
        
        return {
            'is_authenticated': self.is_authenticated,
            'last_activity_time': self.last_activity_time.isoformat(),
            'auto_lock_enabled': self.config.auto_lock_enabled,
            'auto_lock_timeout_minutes': self.config.auto_lock_timeout_minutes,
            'security_level': self.config.security_level.value,
            'biometric_auth': self.biometric_auth.get_auth_metrics(),
            'secure_storage': self.secure_storage.get_storage_metrics()
        }
    
    async def shutdown(self):
        """Shutdown mobile security"""
        
        if self.auto_lock_task and not self.auto_lock_task.done():
            self.auto_lock_task.cancel()
            try:
                await self.auto_lock_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🔐 Mobile Security shutdown complete")
