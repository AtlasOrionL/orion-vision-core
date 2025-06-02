"""
Authentication Manager for Orion Vision Core

This module provides comprehensive authentication and session management.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.2 - Advanced Features & Enhanced Capabilities
"""

import time
import hashlib
import secrets
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType, MetricLevel


class AuthMethod(Enum):
    """Authentication method enumeration"""
    PASSWORD = "password"
    TOKEN = "token"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    BIOMETRIC = "biometric"
    MULTI_FACTOR = "multi_factor"


class UserRole(Enum):
    """User role enumeration"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SYSTEM = "system"


class SessionStatus(Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


@dataclass
class User:
    """User data structure"""
    user_id: str
    username: str
    email: str
    role: UserRole
    password_hash: Optional[str] = None
    api_keys: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_login: Optional[float] = None
    login_attempts: int = 0
    is_locked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate user after initialization"""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        if not self.username:
            raise ValueError("username cannot be empty")
        if not self.email:
            raise ValueError("email cannot be empty")


@dataclass
class Session:
    """Session data structure"""
    session_id: str
    user_id: str
    auth_method: AuthMethod
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 3600)  # 1 hour
    status: SessionStatus = SessionStatus.ACTIVE
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if session is valid"""
        return (self.status == SessionStatus.ACTIVE and 
                time.time() < self.expires_at)
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return time.time() >= self.expires_at
    
    def extend_session(self, duration: float = 3600.0):
        """Extend session duration"""
        self.expires_at = time.time() + duration
        self.last_activity = time.time()


class AuthenticationManager:
    """
    Comprehensive authentication and session management system
    
    Provides secure user authentication, session management, and access control.
    """
    
    def __init__(self, secret_key: Optional[str] = None, 
                 metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize authentication manager"""
        self.logger = logger or AgentLogger("auth_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Security configuration
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.session_timeout = 3600.0  # 1 hour
        self.max_login_attempts = 5
        self.lockout_duration = 900.0  # 15 minutes
        
        # User and session storage
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.username_to_user_id: Dict[str, str] = {}
        self.email_to_user_id: Dict[str, str] = {}
        
        # Security tracking
        self.failed_login_attempts: Dict[str, List[float]] = {}
        self.active_sessions_by_user: Dict[str, List[str]] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.auth_stats = {
            'total_users': 0,
            'active_sessions': 0,
            'successful_logins': 0,
            'failed_logins': 0,
            'locked_accounts': 0,
            'revoked_sessions': 0
        }
        
        self.logger.info("Authentication Manager initialized")
    
    def create_user(self, username: str, email: str, password: str, 
                   role: UserRole = UserRole.USER, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new user"""
        try:
            with self._lock:
                # Check if username or email already exists
                if username in self.username_to_user_id:
                    raise ValueError(f"Username '{username}' already exists")
                if email in self.email_to_user_id:
                    raise ValueError(f"Email '{email}' already exists")
                
                # Generate user ID
                user_id = secrets.token_urlsafe(16)
                
                # Hash password
                password_hash = self._hash_password(password)
                
                # Create user
                user = User(
                    user_id=user_id,
                    username=username,
                    email=email,
                    role=role,
                    password_hash=password_hash,
                    metadata=metadata or {}
                )
                
                # Store user
                self.users[user_id] = user
                self.username_to_user_id[username] = user_id
                self.email_to_user_id[email] = user_id
                
                # Update statistics
                self.auth_stats['total_users'] += 1
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="auth.user_created",
                    value=1,
                    metric_type=MetricType.COUNTER,
                    tags={'role': role.value}
                )
                
                self.logger.info(
                    "User created successfully",
                    user_id=user_id,
                    username=username,
                    role=role.value
                )
                
                return user_id
                
        except Exception as e:
            self.logger.error("Failed to create user", username=username, error=str(e))
            raise
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None) -> Optional[str]:
        """Authenticate user and create session"""
        start_time = time.time()
        
        try:
            with self._lock:
                # Check if user exists
                if username not in self.username_to_user_id:
                    self._record_failed_login(username, "user_not_found")
                    return None
                
                user_id = self.username_to_user_id[username]
                user = self.users[user_id]
                
                # Check if account is locked
                if user.is_locked:
                    self._record_failed_login(username, "account_locked")
                    return None
                
                # Check login attempts
                if self._is_account_temporarily_locked(username):
                    self._record_failed_login(username, "too_many_attempts")
                    return None
                
                # Verify password
                if not self._verify_password(password, user.password_hash):
                    self._record_failed_login(username, "invalid_password")
                    user.login_attempts += 1
                    
                    # Lock account if too many attempts
                    if user.login_attempts >= self.max_login_attempts:
                        user.is_locked = True
                        self.auth_stats['locked_accounts'] += 1
                        
                        self.logger.warning(
                            "Account locked due to too many failed attempts",
                            username=username,
                            attempts=user.login_attempts
                        )
                    
                    return None
                
                # Successful authentication
                session_id = self._create_session(user_id, AuthMethod.PASSWORD, ip_address, user_agent)
                
                # Update user
                user.last_login = time.time()
                user.login_attempts = 0
                
                # Clear failed attempts
                if username in self.failed_login_attempts:
                    del self.failed_login_attempts[username]
                
                # Update statistics
                self.auth_stats['successful_logins'] += 1
                
                # Collect metrics
                auth_time = (time.time() - start_time) * 1000
                self.metrics_collector.collect_metric(
                    name="auth.login_time",
                    value=auth_time,
                    metric_type=MetricType.TIMER,
                    tags={'method': 'password', 'result': 'success'}
                )
                
                self.logger.info(
                    "User authenticated successfully",
                    username=username,
                    session_id=session_id,
                    auth_time_ms=f"{auth_time:.2f}"
                )
                
                return session_id
                
        except Exception as e:
            self.logger.error("Authentication failed", username=username, error=str(e))
            return None
    
    def validate_session(self, session_id: str) -> Optional[User]:
        """Validate session and return user"""
        try:
            with self._lock:
                if session_id not in self.sessions:
                    return None
                
                session = self.sessions[session_id]
                
                # Check if session is valid
                if not session.is_valid():
                    if session.is_expired():
                        session.status = SessionStatus.EXPIRED
                        self._cleanup_expired_session(session_id)
                    return None
                
                # Update last activity
                session.last_activity = time.time()
                
                # Get user
                user = self.users.get(session.user_id)
                if not user:
                    self._revoke_session(session_id)
                    return None
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="auth.session_validation",
                    value=1,
                    metric_type=MetricType.COUNTER,
                    tags={'result': 'success'}
                )
                
                return user
                
        except Exception as e:
            self.logger.error("Session validation failed", session_id=session_id, error=str(e))
            return None
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke a session"""
        return self._revoke_session(session_id)
    
    def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user"""
        try:
            with self._lock:
                if user_id not in self.active_sessions_by_user:
                    return 0
                
                session_ids = list(self.active_sessions_by_user[user_id])
                revoked_count = 0
                
                for session_id in session_ids:
                    if self._revoke_session(session_id):
                        revoked_count += 1
                
                self.logger.info(
                    "All user sessions revoked",
                    user_id=user_id,
                    revoked_count=revoked_count
                )
                
                return revoked_count
                
        except Exception as e:
            self.logger.error("Failed to revoke user sessions", user_id=user_id, error=str(e))
            return 0
    
    def generate_api_key(self, user_id: str) -> Optional[str]:
        """Generate API key for user"""
        try:
            with self._lock:
                if user_id not in self.users:
                    return None
                
                user = self.users[user_id]
                api_key = f"ak_{secrets.token_urlsafe(32)}"
                
                user.api_keys.append(api_key)
                
                self.logger.info("API key generated", user_id=user_id)
                return api_key
                
        except Exception as e:
            self.logger.error("Failed to generate API key", user_id=user_id, error=str(e))
            return None
    
    def validate_api_key(self, api_key: str) -> Optional[User]:
        """Validate API key and return user"""
        try:
            with self._lock:
                for user in self.users.values():
                    if api_key in user.api_keys:
                        # Collect metrics
                        self.metrics_collector.collect_metric(
                            name="auth.api_key_validation",
                            value=1,
                            metric_type=MetricType.COUNTER,
                            tags={'result': 'success'}
                        )
                        return user
                
                # API key not found
                self.metrics_collector.collect_metric(
                    name="auth.api_key_validation",
                    value=1,
                    metric_type=MetricType.COUNTER,
                    tags={'result': 'failed'}
                )
                return None
                
        except Exception as e:
            self.logger.error("API key validation failed", error=str(e))
            return None
    
    def _create_session(self, user_id: str, auth_method: AuthMethod,
                       ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        """Create a new session"""
        session_id = secrets.token_urlsafe(32)
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            auth_method=auth_method,
            expires_at=time.time() + self.session_timeout,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Store session
        self.sessions[session_id] = session
        
        # Track active sessions by user
        if user_id not in self.active_sessions_by_user:
            self.active_sessions_by_user[user_id] = []
        self.active_sessions_by_user[user_id].append(session_id)
        
        # Update statistics
        self.auth_stats['active_sessions'] += 1
        
        return session_id
    
    def _revoke_session(self, session_id: str) -> bool:
        """Revoke a session"""
        try:
            with self._lock:
                if session_id not in self.sessions:
                    return False
                
                session = self.sessions[session_id]
                session.status = SessionStatus.REVOKED
                
                # Remove from active sessions
                user_id = session.user_id
                if user_id in self.active_sessions_by_user:
                    if session_id in self.active_sessions_by_user[user_id]:
                        self.active_sessions_by_user[user_id].remove(session_id)
                
                # Update statistics
                self.auth_stats['active_sessions'] -= 1
                self.auth_stats['revoked_sessions'] += 1
                
                self.logger.info("Session revoked", session_id=session_id, user_id=user_id)
                return True
                
        except Exception as e:
            self.logger.error("Failed to revoke session", session_id=session_id, error=str(e))
            return False
    
    def _cleanup_expired_session(self, session_id: str):
        """Clean up expired session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            user_id = session.user_id
            
            # Remove from active sessions
            if user_id in self.active_sessions_by_user:
                if session_id in self.active_sessions_by_user[user_id]:
                    self.active_sessions_by_user[user_id].remove(session_id)
            
            # Update statistics
            self.auth_stats['active_sessions'] -= 1
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_hex = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash_check.hex() == hash_hex
        except:
            return False
    
    def _record_failed_login(self, username: str, reason: str):
        """Record failed login attempt"""
        current_time = time.time()
        
        if username not in self.failed_login_attempts:
            self.failed_login_attempts[username] = []
        
        self.failed_login_attempts[username].append(current_time)
        
        # Clean old attempts (older than lockout duration)
        cutoff_time = current_time - self.lockout_duration
        self.failed_login_attempts[username] = [
            attempt for attempt in self.failed_login_attempts[username]
            if attempt > cutoff_time
        ]
        
        # Update statistics
        self.auth_stats['failed_logins'] += 1
        
        # Collect metrics
        self.metrics_collector.collect_metric(
            name="auth.failed_login",
            value=1,
            metric_type=MetricType.COUNTER,
            tags={'reason': reason}
        )
        
        self.logger.warning(
            "Failed login attempt",
            username=username,
            reason=reason,
            attempts_count=len(self.failed_login_attempts[username])
        )
    
    def _is_account_temporarily_locked(self, username: str) -> bool:
        """Check if account is temporarily locked due to failed attempts"""
        if username not in self.failed_login_attempts:
            return False
        
        current_time = time.time()
        cutoff_time = current_time - self.lockout_duration
        
        # Count recent failed attempts
        recent_attempts = [
            attempt for attempt in self.failed_login_attempts[username]
            if attempt > cutoff_time
        ]
        
        return len(recent_attempts) >= self.max_login_attempts
    
    def get_auth_stats(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        with self._lock:
            return {
                'auth_enabled': True,
                'session_timeout': self.session_timeout,
                'max_login_attempts': self.max_login_attempts,
                'lockout_duration': self.lockout_duration,
                'stats': self.auth_stats.copy()
            }
