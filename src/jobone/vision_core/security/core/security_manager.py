"""
Security Manager for Orion Vision Core

This module provides comprehensive security management including
authentication, authorization, encryption, and threat detection.
Part of Sprint 9.7 Advanced Security & Compliance development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.7 - Advanced Security & Compliance
"""

import time
import threading
import json
import hashlib
import secrets
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class SecurityLevel(Enum):
    """Security level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    MAXIMUM = "maximum"


class ThreatLevel(Enum):
    """Threat level enumeration"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthenticationMethod(Enum):
    """Authentication method enumeration"""
    PASSWORD = "password"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    BIOMETRIC = "biometric"
    MULTI_FACTOR = "multi_factor"
    SSO = "sso"


class EncryptionAlgorithm(Enum):
    """Encryption algorithm enumeration"""
    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20 = "chacha20"
    ELLIPTIC_CURVE = "elliptic_curve"


@dataclass
class SecurityPolicy:
    """Security policy data structure"""
    policy_id: str
    policy_name: str
    security_level: SecurityLevel
    rules: List[Dict[str, Any]] = field(default_factory=list)
    enforcement_mode: str = "strict"  # strict, permissive, monitor
    exceptions: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def validate(self) -> bool:
        """Validate security policy"""
        if not self.policy_name or not self.policy_id:
            return False
        if not self.rules:
            return False
        return True


@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: str
    threat_level: ThreatLevel
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False
    
    def get_age_minutes(self) -> float:
        """Get event age in minutes"""
        return (time.time() - self.timestamp) / 60


@dataclass
class AccessToken:
    """Access token data structure"""
    token_id: str
    user_id: str
    token_value: str
    permissions: List[str] = field(default_factory=list)
    expires_at: float = 0.0
    created_at: float = field(default_factory=time.time)
    last_used: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return time.time() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if token is valid"""
        return not self.is_expired() and self.token_value


class SecurityManager:
    """
    Comprehensive security management system
    
    Provides authentication, authorization, encryption, threat detection,
    and security policy enforcement with real-time monitoring.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize security manager"""
        self.logger = logger or AgentLogger("security_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Security policies and events
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.security_events: Dict[str, SecurityEvent] = {}
        self.access_tokens: Dict[str, AccessToken] = {}
        
        # Authentication and authorization
        self.authenticated_users: Dict[str, Dict[str, Any]] = {}
        self.user_permissions: Dict[str, List[str]] = {}
        self.failed_attempts: Dict[str, List[float]] = {}
        
        # Encryption keys
        self.encryption_keys: Dict[str, str] = {}
        
        # Configuration
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 30
        self.token_expiry_hours = 24
        self.password_min_length = 8
        self.require_mfa = False
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.security_stats = {
            'total_policies': 0,
            'active_policies': 0,
            'security_events': 0,
            'critical_events': 0,
            'authentication_attempts': 0,
            'successful_authentications': 0,
            'failed_authentications': 0,
            'active_tokens': 0,
            'threat_detections': 0,
            'policy_violations': 0
        }
        
        # Initialize default security policies
        self._initialize_default_policies()
        
        self.logger.info("Security Manager initialized")
    
    def _initialize_default_policies(self):
        """Initialize default security policies"""
        # Default authentication policy
        auth_policy = SecurityPolicy(
            policy_id="default_auth",
            policy_name="Default Authentication Policy",
            security_level=SecurityLevel.HIGH,
            rules=[
                {"type": "password_complexity", "min_length": 8, "require_special": True},
                {"type": "max_failed_attempts", "limit": 5},
                {"type": "session_timeout", "minutes": 60}
            ]
        )
        self.create_security_policy(auth_policy)
        
        # Default access control policy
        access_policy = SecurityPolicy(
            policy_id="default_access",
            policy_name="Default Access Control Policy",
            security_level=SecurityLevel.MEDIUM,
            rules=[
                {"type": "role_based_access", "enabled": True},
                {"type": "resource_permissions", "strict": True},
                {"type": "audit_logging", "enabled": True}
            ]
        )
        self.create_security_policy(access_policy)
    
    def create_security_policy(self, policy: SecurityPolicy) -> bool:
        """Create security policy"""
        try:
            # Validate policy
            if not policy.validate():
                self.logger.error("Invalid security policy", policy_id=policy.policy_id)
                return False
            
            with self._lock:
                # Store policy
                self.security_policies[policy.policy_id] = policy
                
                # Update statistics
                self.security_stats['total_policies'] = len(self.security_policies)
                self.security_stats['active_policies'] = sum(
                    1 for p in self.security_policies.values() 
                    if p.enforcement_mode != "disabled"
                )
            
            self.logger.info(
                "Security policy created",
                policy_id=policy.policy_id,
                policy_name=policy.policy_name,
                security_level=policy.security_level.value,
                rules_count=len(policy.rules)
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Security policy creation failed", policy_id=policy.policy_id, error=str(e))
            return False
    
    def authenticate_user(self, user_id: str, credentials: Dict[str, Any], 
                         method: AuthenticationMethod = AuthenticationMethod.PASSWORD) -> Optional[str]:
        """Authenticate user and return access token"""
        try:
            # Check for account lockout
            if self._is_account_locked(user_id):
                self._log_security_event(
                    "authentication_blocked",
                    ThreatLevel.MEDIUM,
                    user_id=user_id,
                    details={"reason": "account_locked"}
                )
                return None
            
            # Perform authentication based on method
            auth_success = False
            
            if method == AuthenticationMethod.PASSWORD:
                auth_success = self._authenticate_password(user_id, credentials.get("password", ""))
            elif method == AuthenticationMethod.TOKEN:
                auth_success = self._authenticate_token(credentials.get("token", ""))
            elif method == AuthenticationMethod.MULTI_FACTOR:
                auth_success = self._authenticate_mfa(user_id, credentials)
            else:
                # Mock authentication for other methods
                auth_success = True
            
            with self._lock:
                self.security_stats['authentication_attempts'] += 1
            
            if auth_success:
                # Generate access token
                token = self._generate_access_token(user_id)
                
                # Store authenticated user
                with self._lock:
                    self.authenticated_users[user_id] = {
                        'authenticated_at': time.time(),
                        'method': method.value,
                        'token': token.token_value
                    }
                    
                    # Clear failed attempts
                    if user_id in self.failed_attempts:
                        del self.failed_attempts[user_id]
                    
                    self.security_stats['successful_authentications'] += 1
                
                self.logger.info(
                    "User authenticated successfully",
                    user_id=user_id,
                    method=method.value,
                    token_id=token.token_id
                )
                
                return token.token_value
            else:
                # Record failed attempt
                self._record_failed_attempt(user_id)
                
                with self._lock:
                    self.security_stats['failed_authentications'] += 1
                
                self._log_security_event(
                    "authentication_failed",
                    ThreatLevel.MEDIUM,
                    user_id=user_id,
                    details={"method": method.value}
                )
                
                return None
                
        except Exception as e:
            self.logger.error("Authentication failed", user_id=user_id, error=str(e))
            return None
    
    def _authenticate_password(self, user_id: str, password: str) -> bool:
        """Authenticate using password"""
        # Mock password authentication
        if len(password) >= self.password_min_length:
            # Simulate password hash verification
            expected_hash = hashlib.sha256(f"{user_id}_password".encode()).hexdigest()
            provided_hash = hashlib.sha256(password.encode()).hexdigest()
            return len(password) >= 8  # Mock validation
        return False
    
    def _authenticate_token(self, token_value: str) -> bool:
        """Authenticate using token"""
        for token in self.access_tokens.values():
            if token.token_value == token_value and token.is_valid():
                token.last_used = time.time()
                return True
        return False
    
    def _authenticate_mfa(self, user_id: str, credentials: Dict[str, Any]) -> bool:
        """Authenticate using multi-factor authentication"""
        password_valid = self._authenticate_password(user_id, credentials.get("password", ""))
        mfa_code_valid = credentials.get("mfa_code") == "123456"  # Mock MFA
        return password_valid and mfa_code_valid
    
    def _generate_access_token(self, user_id: str) -> AccessToken:
        """Generate access token for user"""
        token_id = str(uuid.uuid4())
        token_value = secrets.token_urlsafe(32)
        expires_at = time.time() + (self.token_expiry_hours * 3600)
        
        # Get user permissions
        permissions = self.user_permissions.get(user_id, ["read"])
        
        token = AccessToken(
            token_id=token_id,
            user_id=user_id,
            token_value=token_value,
            permissions=permissions,
            expires_at=expires_at
        )
        
        with self._lock:
            self.access_tokens[token_id] = token
            self.security_stats['active_tokens'] = len([
                t for t in self.access_tokens.values() if t.is_valid()
            ])
        
        return token
    
    def authorize_access(self, token_value: str, resource: str, action: str) -> bool:
        """Authorize access to resource"""
        try:
            # Find token
            token = None
            for t in self.access_tokens.values():
                if t.token_value == token_value:
                    token = t
                    break
            
            if not token or not token.is_valid():
                self._log_security_event(
                    "authorization_failed",
                    ThreatLevel.MEDIUM,
                    details={"reason": "invalid_token", "resource": resource, "action": action}
                )
                return False
            
            # Check permissions
            required_permission = f"{action}:{resource}"
            has_permission = (
                "admin" in token.permissions or
                required_permission in token.permissions or
                action in token.permissions
            )
            
            if has_permission:
                token.last_used = time.time()
                
                self.logger.debug(
                    "Access authorized",
                    user_id=token.user_id,
                    resource=resource,
                    action=action
                )
                
                return True
            else:
                self._log_security_event(
                    "authorization_denied",
                    ThreatLevel.MEDIUM,
                    user_id=token.user_id,
                    resource=resource,
                    action=action,
                    details={"reason": "insufficient_permissions"}
                )
                
                return False
                
        except Exception as e:
            self.logger.error("Authorization check failed", resource=resource, action=action, error=str(e))
            return False
    
    def encrypt_data(self, data: str, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256) -> str:
        """Encrypt data using specified algorithm"""
        try:
            # Mock encryption - in production, use proper encryption libraries
            key = self._get_encryption_key(algorithm)
            
            # Simple mock encryption (NOT for production use)
            encrypted = hashlib.sha256(f"{key}:{data}".encode()).hexdigest()
            
            self.logger.debug(
                "Data encrypted",
                algorithm=algorithm.value,
                data_length=len(data)
            )
            
            return f"encrypted:{algorithm.value}:{encrypted}"
            
        except Exception as e:
            self.logger.error("Data encryption failed", algorithm=algorithm.value, error=str(e))
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        try:
            if not encrypted_data.startswith("encrypted:"):
                return encrypted_data
            
            # Mock decryption
            parts = encrypted_data.split(":", 3)
            if len(parts) >= 3:
                algorithm = parts[1]
                encrypted_hash = parts[2]
                
                self.logger.debug(
                    "Data decrypted",
                    algorithm=algorithm
                )
                
                return f"decrypted_data_from_{algorithm}"
            
            return encrypted_data
            
        except Exception as e:
            self.logger.error("Data decryption failed", error=str(e))
            return encrypted_data
    
    def _get_encryption_key(self, algorithm: EncryptionAlgorithm) -> str:
        """Get encryption key for algorithm"""
        key_name = f"key_{algorithm.value}"
        
        if key_name not in self.encryption_keys:
            # Generate new key
            self.encryption_keys[key_name] = secrets.token_hex(32)
        
        return self.encryption_keys[key_name]
    
    def detect_threat(self, event_data: Dict[str, Any]) -> Optional[ThreatLevel]:
        """Detect security threats"""
        try:
            threat_level = ThreatLevel.NONE
            
            # Check for suspicious patterns
            if event_data.get("failed_attempts", 0) > 3:
                threat_level = ThreatLevel.MEDIUM
            
            if event_data.get("source_ip") in ["192.168.1.100", "10.0.0.50"]:  # Mock suspicious IPs
                threat_level = ThreatLevel.HIGH
            
            if event_data.get("action") == "admin_access" and event_data.get("time") == "night":
                threat_level = ThreatLevel.HIGH
            
            if threat_level != ThreatLevel.NONE:
                self._log_security_event(
                    "threat_detected",
                    threat_level,
                    source_ip=event_data.get("source_ip"),
                    details=event_data
                )
                
                with self._lock:
                    self.security_stats['threat_detections'] += 1
            
            return threat_level
            
        except Exception as e:
            self.logger.error("Threat detection failed", error=str(e))
            return None
    
    def _log_security_event(self, event_type: str, threat_level: ThreatLevel, 
                           source_ip: Optional[str] = None, user_id: Optional[str] = None,
                           resource: Optional[str] = None, action: Optional[str] = None,
                           details: Optional[Dict[str, Any]] = None):
        """Log security event"""
        event_id = str(uuid.uuid4())
        
        event = SecurityEvent(
            event_id=event_id,
            event_type=event_type,
            threat_level=threat_level,
            source_ip=source_ip,
            user_id=user_id,
            resource=resource,
            action=action,
            details=details or {}
        )
        
        with self._lock:
            self.security_events[event_id] = event
            self.security_stats['security_events'] += 1
            
            if threat_level == ThreatLevel.CRITICAL:
                self.security_stats['critical_events'] += 1
        
        # Collect metrics
        self.metrics_collector.collect_metric(
            name="security.event_logged",
            value=1,
            metric_type=MetricType.COUNTER,
            tags={
                'event_type': event_type,
                'threat_level': threat_level.value
            }
        )
        
        self.logger.warning(
            "Security event logged",
            event_id=event_id,
            event_type=event_type,
            threat_level=threat_level.value,
            source_ip=source_ip,
            user_id=user_id
        )
    
    def _is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if user_id not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[user_id]
        if len(attempts) < self.max_failed_attempts:
            return False
        
        # Check if lockout period has expired
        last_attempt = max(attempts)
        lockout_expires = last_attempt + (self.lockout_duration_minutes * 60)
        
        return time.time() < lockout_expires
    
    def _record_failed_attempt(self, user_id: str):
        """Record failed authentication attempt"""
        current_time = time.time()
        
        with self._lock:
            if user_id not in self.failed_attempts:
                self.failed_attempts[user_id] = []
            
            self.failed_attempts[user_id].append(current_time)
            
            # Keep only recent attempts (within lockout window)
            cutoff_time = current_time - (self.lockout_duration_minutes * 60)
            self.failed_attempts[user_id] = [
                t for t in self.failed_attempts[user_id] if t > cutoff_time
            ]
    
    def set_user_permissions(self, user_id: str, permissions: List[str]):
        """Set user permissions"""
        with self._lock:
            self.user_permissions[user_id] = permissions
        
        self.logger.info(
            "User permissions updated",
            user_id=user_id,
            permissions=permissions
        )
    
    def revoke_token(self, token_value: str) -> bool:
        """Revoke access token"""
        try:
            for token_id, token in self.access_tokens.items():
                if token.token_value == token_value:
                    with self._lock:
                        del self.access_tokens[token_id]
                        self.security_stats['active_tokens'] = len([
                            t for t in self.access_tokens.values() if t.is_valid()
                        ])
                    
                    self.logger.info(
                        "Access token revoked",
                        token_id=token_id,
                        user_id=token.user_id
                    )
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error("Token revocation failed", error=str(e))
            return False
    
    def get_security_events(self, threat_level_filter: Optional[ThreatLevel] = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get security events with optional filtering"""
        events = []
        
        for event in self.security_events.values():
            if threat_level_filter is None or event.threat_level == threat_level_filter:
                events.append({
                    'event_id': event.event_id,
                    'event_type': event.event_type,
                    'threat_level': event.threat_level.value,
                    'source_ip': event.source_ip,
                    'user_id': event.user_id,
                    'resource': event.resource,
                    'action': event.action,
                    'timestamp': event.timestamp,
                    'age_minutes': event.get_age_minutes(),
                    'resolved': event.resolved
                })
        
        # Sort by timestamp (newest first) and limit
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        return events[:limit]
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security manager statistics"""
        with self._lock:
            # Calculate additional metrics
            active_tokens = len([t for t in self.access_tokens.values() if t.is_valid()])
            
            return {
                'total_policies': len(self.security_policies),
                'total_events': len(self.security_events),
                'active_tokens': active_tokens,
                'authenticated_users': len(self.authenticated_users),
                'locked_accounts': len([
                    user_id for user_id in self.failed_attempts.keys()
                    if self._is_account_locked(user_id)
                ]),
                'encryption_keys': len(self.encryption_keys),
                'max_failed_attempts': self.max_failed_attempts,
                'lockout_duration_minutes': self.lockout_duration_minutes,
                'token_expiry_hours': self.token_expiry_hours,
                'require_mfa': self.require_mfa,
                'stats': self.security_stats.copy()
            }
