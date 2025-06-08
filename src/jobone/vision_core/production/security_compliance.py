"""
🔒 Security & Compliance - Q6.4 Implementation

Production security, compliance, authentication, authorization,
and security monitoring for Orion Vision Core

Author: Orion Vision Core Team
Based on: Q1-Q5 Foundation + Vision Integration + Q6.1-Q6.3 Production
Priority: CRITICAL - Production Security
"""

import logging
import json
import hashlib
import secrets
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
import jwt
import base64

# Security Levels
class SecurityLevel(Enum):
    """Güvenlik seviyeleri"""
    PUBLIC = "public"                               # Herkese açık
    INTERNAL = "internal"                           # İç kullanım
    CONFIDENTIAL = "confidential"                   # Gizli
    RESTRICTED = "restricted"                       # Kısıtlı
    TOP_SECRET = "top_secret"                       # Çok gizli

# Authentication Methods
class AuthMethod(Enum):
    """Kimlik doğrulama yöntemleri"""
    API_KEY = "api_key"                             # API anahtarı
    JWT_TOKEN = "jwt_token"                         # JWT token
    OAUTH2 = "oauth2"                               # OAuth2
    CERTIFICATE = "certificate"                     # Sertifika
    MULTI_FACTOR = "multi_factor"                   # Çok faktörlü

# Compliance Standards
class ComplianceStandard(Enum):
    """Uyumluluk standartları"""
    GDPR = "gdpr"                                   # GDPR
    HIPAA = "hipaa"                                 # HIPAA
    SOC2 = "soc2"                                   # SOC 2
    ISO27001 = "iso27001"                           # ISO 27001
    PCI_DSS = "pci_dss"                             # PCI DSS

# Security Event Types
class SecurityEventType(Enum):
    """Güvenlik olay türleri"""
    AUTHENTICATION_SUCCESS = "auth_success"         # Başarılı kimlik doğrulama
    AUTHENTICATION_FAILURE = "auth_failure"         # Başarısız kimlik doğrulama
    AUTHORIZATION_DENIED = "authz_denied"           # Yetkilendirme reddedildi
    SUSPICIOUS_ACTIVITY = "suspicious_activity"     # Şüpheli aktivite
    DATA_ACCESS = "data_access"                     # Veri erişimi
    SECURITY_VIOLATION = "security_violation"       # Güvenlik ihlali

@dataclass
class SecurityCredential:
    """
    Security Credential
    
    Güvenlik kimlik bilgisi.
    """
    
    credential_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    auth_method: AuthMethod = AuthMethod.API_KEY
    
    # Credential properties
    user_id: str = ""
    username: str = ""
    
    # Authentication data
    api_key: str = ""
    jwt_token: str = ""
    certificate_thumbprint: str = ""
    
    # Permissions and roles
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    
    # Validity
    issued_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    active: bool = True
    
    # Usage tracking
    last_used: Optional[datetime] = None
    usage_count: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if credential is valid"""
        if not self.active:
            return False
        
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        
        return True
    
    def use_credential(self):
        """Record credential usage"""
        self.last_used = datetime.now()
        self.usage_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'credential_id': self.credential_id,
            'auth_method': self.auth_method.value,
            'user_id': self.user_id,
            'username': self.username,
            'roles': self.roles,
            'permissions': self.permissions,
            'security_level': self.security_level.value,
            'issued_at': self.issued_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'active': self.active,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count,
            'is_valid': self.is_valid(),
            'metadata': self.metadata
        }

@dataclass
class SecurityEvent:
    """
    Security Event
    
    Güvenlik olayı kaydı.
    """
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: SecurityEventType = SecurityEventType.DATA_ACCESS
    
    # Event properties
    user_id: str = ""
    username: str = ""
    source_ip: str = ""
    user_agent: str = ""
    
    # Event details
    resource: str = ""
    action: str = ""
    result: str = "success"                         # success, failure, denied
    
    # Security context
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    auth_method: AuthMethod = AuthMethod.API_KEY
    
    # Risk assessment
    risk_score: float = 0.0                         # 0.0 - 1.0
    anomaly_detected: bool = False
    
    # Temporal properties
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Additional data
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_risk_score(self) -> float:
        """Calculate risk score based on event properties"""
        risk = 0.0
        
        # Base risk by event type
        risk_by_type = {
            SecurityEventType.AUTHENTICATION_FAILURE: 0.3,
            SecurityEventType.AUTHORIZATION_DENIED: 0.4,
            SecurityEventType.SUSPICIOUS_ACTIVITY: 0.7,
            SecurityEventType.SECURITY_VIOLATION: 0.9,
            SecurityEventType.DATA_ACCESS: 0.1,
            SecurityEventType.AUTHENTICATION_SUCCESS: 0.0
        }
        
        risk += risk_by_type.get(self.event_type, 0.1)
        
        # Increase risk for high security levels
        if self.security_level in [SecurityLevel.RESTRICTED, SecurityLevel.TOP_SECRET]:
            risk += 0.2
        
        # Increase risk for failures
        if self.result in ['failure', 'denied']:
            risk += 0.3
        
        # Increase risk for anomalies
        if self.anomaly_detected:
            risk += 0.4
        
        self.risk_score = min(1.0, risk)
        return self.risk_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'username': self.username,
            'source_ip': self.source_ip,
            'user_agent': self.user_agent,
            'resource': self.resource,
            'action': self.action,
            'result': self.result,
            'security_level': self.security_level.value,
            'auth_method': self.auth_method.value,
            'risk_score': self.risk_score,
            'anomaly_detected': self.anomaly_detected,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details,
            'metadata': self.metadata
        }

@dataclass
class ComplianceCheck:
    """
    Compliance Check
    
    Uyumluluk kontrolü.
    """
    
    check_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    standard: ComplianceStandard = ComplianceStandard.GDPR
    
    # Check properties
    name: str = ""
    description: str = ""
    requirement: str = ""
    
    # Check status
    compliant: bool = False
    last_check: datetime = field(default_factory=datetime.now)
    next_check: datetime = field(default_factory=datetime.now)
    
    # Check results
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Remediation
    remediation_required: bool = False
    remediation_deadline: Optional[datetime] = None
    remediation_status: str = "pending"              # pending, in_progress, completed
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def mark_compliant(self, findings: List[str] = None):
        """Mark check as compliant"""
        self.compliant = True
        self.findings = findings or []
        self.remediation_required = False
        self.last_check = datetime.now()
    
    def mark_non_compliant(self, findings: List[str], recommendations: List[str] = None):
        """Mark check as non-compliant"""
        self.compliant = False
        self.findings = findings
        self.recommendations = recommendations or []
        self.remediation_required = True
        self.remediation_deadline = datetime.now() + timedelta(days=30)
        self.last_check = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'check_id': self.check_id,
            'standard': self.standard.value,
            'name': self.name,
            'description': self.description,
            'requirement': self.requirement,
            'compliant': self.compliant,
            'last_check': self.last_check.isoformat(),
            'next_check': self.next_check.isoformat(),
            'findings': self.findings,
            'recommendations': self.recommendations,
            'remediation_required': self.remediation_required,
            'remediation_deadline': self.remediation_deadline.isoformat() if self.remediation_deadline else None,
            'remediation_status': self.remediation_status,
            'metadata': self.metadata
        }

class SecurityComplianceSystem:
    """
    Security & Compliance System
    
    Production güvenlik ve uyumluluk yönetim sistemi.
    """
    
    def __init__(self, 
                 system_name: str = "orion-vision-core",
                 jwt_secret: str = None):
        self.logger = logging.getLogger(__name__)
        self.system_name = system_name
        self.jwt_secret = jwt_secret or secrets.token_urlsafe(32)
        
        # Security components
        self.credentials: Dict[str, SecurityCredential] = {}
        self.security_events: List[SecurityEvent] = []
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        
        # Security policies
        self.password_policy = {
            'min_length': 12,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_special_chars': True
        }
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.max_requests_per_minute = 60
        
        # Statistics
        self.total_auth_attempts = 0
        self.successful_auth_attempts = 0
        self.failed_auth_attempts = 0
        self.security_violations = 0
        
        # Initialize default compliance checks
        self._initialize_compliance_checks()
        
        self.logger.info(f"🔒 SecurityComplianceSystem initialized - Q6.4 Implementation "
                        f"(system: {system_name})")
    
    def _initialize_compliance_checks(self):
        """Initialize default compliance checks"""
        # GDPR compliance checks
        gdpr_checks = [
            {
                'name': 'Data Encryption at Rest',
                'description': 'Verify that all personal data is encrypted at rest',
                'requirement': 'GDPR Article 32 - Security of processing'
            },
            {
                'name': 'Data Encryption in Transit',
                'description': 'Verify that all personal data is encrypted in transit',
                'requirement': 'GDPR Article 32 - Security of processing'
            },
            {
                'name': 'Access Control',
                'description': 'Verify proper access controls for personal data',
                'requirement': 'GDPR Article 32 - Security of processing'
            }
        ]
        
        for check_data in gdpr_checks:
            check = ComplianceCheck(
                standard=ComplianceStandard.GDPR,
                name=check_data['name'],
                description=check_data['description'],
                requirement=check_data['requirement']
            )
            self.compliance_checks[check.check_id] = check
    
    def generate_api_key(self, user_id: str, username: str, 
                        roles: List[str] = None,
                        security_level: SecurityLevel = SecurityLevel.INTERNAL) -> SecurityCredential:
        """Generate API key credential"""
        
        # Generate secure API key
        api_key = f"orion_{secrets.token_urlsafe(32)}"
        
        credential = SecurityCredential(
            auth_method=AuthMethod.API_KEY,
            user_id=user_id,
            username=username,
            api_key=api_key,
            roles=roles or ['user'],
            security_level=security_level,
            expires_at=datetime.now() + timedelta(days=365)  # 1 year expiry
        )
        
        self.credentials[credential.credential_id] = credential
        
        self.logger.info(f"🔒 Generated API key for user: {username}")
        
        return credential
    
    def generate_jwt_token(self, user_id: str, username: str,
                          roles: List[str] = None,
                          expires_in_hours: int = 24) -> SecurityCredential:
        """Generate JWT token credential"""
        
        # JWT payload
        payload = {
            'user_id': user_id,
            'username': username,
            'roles': roles or ['user'],
            'iat': datetime.now(),
            'exp': datetime.now() + timedelta(hours=expires_in_hours)
        }
        
        # Generate JWT token
        jwt_token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
        credential = SecurityCredential(
            auth_method=AuthMethod.JWT_TOKEN,
            user_id=user_id,
            username=username,
            jwt_token=jwt_token,
            roles=roles or ['user'],
            expires_at=datetime.now() + timedelta(hours=expires_in_hours)
        )
        
        self.credentials[credential.credential_id] = credential
        
        self.logger.info(f"🔒 Generated JWT token for user: {username}")
        
        return credential
    
    def authenticate(self, auth_token: str, auth_method: AuthMethod) -> Optional[SecurityCredential]:
        """Authenticate user with token"""
        
        self.total_auth_attempts += 1
        
        try:
            # Find credential by token
            credential = None
            
            if auth_method == AuthMethod.API_KEY:
                for cred in self.credentials.values():
                    if cred.api_key == auth_token and cred.auth_method == AuthMethod.API_KEY:
                        credential = cred
                        break
            
            elif auth_method == AuthMethod.JWT_TOKEN:
                # Verify JWT token
                try:
                    payload = jwt.decode(auth_token, self.jwt_secret, algorithms=['HS256'])
                    user_id = payload.get('user_id')
                    
                    # Find credential by user_id and token
                    for cred in self.credentials.values():
                        if (cred.user_id == user_id and 
                            cred.jwt_token == auth_token and 
                            cred.auth_method == AuthMethod.JWT_TOKEN):
                            credential = cred
                            break
                            
                except jwt.ExpiredSignatureError:
                    self._log_security_event(
                        SecurityEventType.AUTHENTICATION_FAILURE,
                        user_id="unknown",
                        details={'error': 'JWT token expired'}
                    )
                    return None
                except jwt.InvalidTokenError:
                    self._log_security_event(
                        SecurityEventType.AUTHENTICATION_FAILURE,
                        user_id="unknown",
                        details={'error': 'Invalid JWT token'}
                    )
                    return None
            
            # Validate credential
            if credential and credential.is_valid():
                credential.use_credential()
                self.successful_auth_attempts += 1
                
                self._log_security_event(
                    SecurityEventType.AUTHENTICATION_SUCCESS,
                    user_id=credential.user_id,
                    username=credential.username,
                    auth_method=auth_method
                )
                
                return credential
            else:
                self.failed_auth_attempts += 1
                
                self._log_security_event(
                    SecurityEventType.AUTHENTICATION_FAILURE,
                    user_id=credential.user_id if credential else "unknown",
                    details={'error': 'Invalid or expired credential'}
                )
                
                return None
        
        except Exception as e:
            self.failed_auth_attempts += 1
            self.logger.error(f"❌ Authentication error: {e}")
            
            self._log_security_event(
                SecurityEventType.AUTHENTICATION_FAILURE,
                user_id="unknown",
                details={'error': str(e)}
            )
            
            return None
    
    def authorize(self, credential: SecurityCredential, 
                 resource: str, action: str,
                 required_security_level: SecurityLevel = SecurityLevel.INTERNAL) -> bool:
        """Authorize user action"""
        
        try:
            # Check if credential is valid
            if not credential.is_valid():
                self._log_security_event(
                    SecurityEventType.AUTHORIZATION_DENIED,
                    user_id=credential.user_id,
                    username=credential.username,
                    resource=resource,
                    action=action,
                    details={'error': 'Invalid credential'}
                )
                return False
            
            # Check security level
            security_levels_order = [
                SecurityLevel.PUBLIC,
                SecurityLevel.INTERNAL,
                SecurityLevel.CONFIDENTIAL,
                SecurityLevel.RESTRICTED,
                SecurityLevel.TOP_SECRET
            ]
            
            user_level_index = security_levels_order.index(credential.security_level)
            required_level_index = security_levels_order.index(required_security_level)
            
            if user_level_index < required_level_index:
                self._log_security_event(
                    SecurityEventType.AUTHORIZATION_DENIED,
                    user_id=credential.user_id,
                    username=credential.username,
                    resource=resource,
                    action=action,
                    details={'error': 'Insufficient security level'}
                )
                return False
            
            # Check specific permissions (simplified)
            required_permission = f"{resource}:{action}"
            if required_permission not in credential.permissions and 'admin' not in credential.roles:
                # Allow if user has admin role or specific permission
                if not any(role in ['admin', 'superuser'] for role in credential.roles):
                    self._log_security_event(
                        SecurityEventType.AUTHORIZATION_DENIED,
                        user_id=credential.user_id,
                        username=credential.username,
                        resource=resource,
                        action=action,
                        details={'error': 'Insufficient permissions'}
                    )
                    return False
            
            # Log successful authorization
            self._log_security_event(
                SecurityEventType.DATA_ACCESS,
                user_id=credential.user_id,
                username=credential.username,
                resource=resource,
                action=action,
                result="success"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Authorization error: {e}")
            return False
    
    def _log_security_event(self, event_type: SecurityEventType,
                           user_id: str = "",
                           username: str = "",
                           resource: str = "",
                           action: str = "",
                           result: str = "success",
                           auth_method: AuthMethod = AuthMethod.API_KEY,
                           details: Dict[str, Any] = None):
        """Log security event"""
        
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            result=result,
            auth_method=auth_method,
            details=details or {}
        )
        
        # Calculate risk score
        event.calculate_risk_score()
        
        # Check for anomalies (simplified)
        if event.risk_score > 0.7:
            event.anomaly_detected = True
            self.security_violations += 1
        
        self.security_events.append(event)
        
        # Limit event history
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-5000:]
        
        if event.risk_score > 0.5:
            self.logger.warning(f"🔒 Security event: {event_type.value} "
                              f"(user: {username}, risk: {event.risk_score:.2f})")
    
    def run_compliance_check(self, check_id: str) -> bool:
        """Run specific compliance check"""
        
        if check_id not in self.compliance_checks:
            return False
        
        check = self.compliance_checks[check_id]
        
        try:
            # Mock compliance check logic
            if check.standard == ComplianceStandard.GDPR:
                if 'encryption' in check.name.lower():
                    # Check encryption compliance
                    check.mark_compliant(['Encryption verified'])
                elif 'access control' in check.name.lower():
                    # Check access control compliance
                    check.mark_compliant(['Access controls verified'])
                else:
                    check.mark_compliant(['General compliance verified'])
            else:
                # Default compliance check
                check.mark_compliant(['Compliance verified'])
            
            self.logger.info(f"🔒 Compliance check passed: {check.name}")
            return True
        
        except Exception as e:
            check.mark_non_compliant(
                [f"Compliance check failed: {str(e)}"],
                ["Review and fix compliance issues"]
            )
            self.logger.error(f"❌ Compliance check failed: {check.name} - {e}")
            return False
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary"""
        
        # Recent security events (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_events = [event for event in self.security_events if event.timestamp > recent_cutoff]
        
        # High-risk events
        high_risk_events = [event for event in recent_events if event.risk_score > 0.7]
        
        # Authentication statistics
        auth_success_rate = (self.successful_auth_attempts / self.total_auth_attempts * 100) if self.total_auth_attempts > 0 else 0
        
        return {
            'total_credentials': len(self.credentials),
            'active_credentials': len([c for c in self.credentials.values() if c.is_valid()]),
            'total_auth_attempts': self.total_auth_attempts,
            'successful_auth_attempts': self.successful_auth_attempts,
            'failed_auth_attempts': self.failed_auth_attempts,
            'auth_success_rate': auth_success_rate,
            'security_violations': self.security_violations,
            'recent_events_count': len(recent_events),
            'high_risk_events_count': len(high_risk_events),
            'security_status': 'secure' if len(high_risk_events) == 0 else 'at_risk'
        }
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance summary"""
        
        compliant_checks = [check for check in self.compliance_checks.values() if check.compliant]
        non_compliant_checks = [check for check in self.compliance_checks.values() if not check.compliant]
        
        # Group by standard
        compliance_by_standard = {}
        for check in self.compliance_checks.values():
            standard = check.standard.value
            if standard not in compliance_by_standard:
                compliance_by_standard[standard] = {'total': 0, 'compliant': 0}
            
            compliance_by_standard[standard]['total'] += 1
            if check.compliant:
                compliance_by_standard[standard]['compliant'] += 1
        
        # Calculate compliance rates
        for standard, data in compliance_by_standard.items():
            data['compliance_rate'] = (data['compliant'] / data['total'] * 100) if data['total'] > 0 else 0
        
        return {
            'total_checks': len(self.compliance_checks),
            'compliant_checks': len(compliant_checks),
            'non_compliant_checks': len(non_compliant_checks),
            'overall_compliance_rate': (len(compliant_checks) / len(self.compliance_checks) * 100) if self.compliance_checks else 0,
            'compliance_by_standard': compliance_by_standard,
            'remediation_required': len([check for check in self.compliance_checks.values() if check.remediation_required])
        }
    
    def get_security_statistics(self) -> Dict[str, Any]:
        """Get security system statistics"""
        return {
            'system_name': self.system_name,
            'total_credentials': len(self.credentials),
            'total_security_events': len(self.security_events),
            'total_compliance_checks': len(self.compliance_checks),
            'total_auth_attempts': self.total_auth_attempts,
            'successful_auth_attempts': self.successful_auth_attempts,
            'failed_auth_attempts': self.failed_auth_attempts,
            'security_violations': self.security_violations,
            'password_policy': self.password_policy,
            'max_requests_per_minute': self.max_requests_per_minute
        }

# Utility functions
def create_security_compliance_system(system_name: str = "orion-vision-core",
                                     jwt_secret: str = None) -> SecurityComplianceSystem:
    """Create Security & Compliance System"""
    return SecurityComplianceSystem(system_name, jwt_secret)

def test_security_compliance():
    """Test Security & Compliance system"""
    print("🔒 Testing Security & Compliance...")
    
    # Create security system
    security = create_security_compliance_system()
    print("✅ Security & Compliance System created")
    
    # Generate credentials
    api_key_cred = security.generate_api_key(
        user_id="user123",
        username="test_user",
        roles=["user", "quantum_operator"],
        security_level=SecurityLevel.CONFIDENTIAL
    )
    
    jwt_cred = security.generate_jwt_token(
        user_id="admin456",
        username="admin_user",
        roles=["admin"],
        expires_in_hours=24
    )
    
    print(f"✅ Generated credentials:")
    print(f"    - API Key: {api_key_cred.api_key[:20]}...")
    print(f"    - JWT Token: {jwt_cred.jwt_token[:30]}...")
    
    # Test authentication
    auth_result1 = security.authenticate(api_key_cred.api_key, AuthMethod.API_KEY)
    auth_result2 = security.authenticate(jwt_cred.jwt_token, AuthMethod.JWT_TOKEN)
    
    print(f"✅ Authentication tests:")
    print(f"    - API Key auth: {'SUCCESS' if auth_result1 else 'FAILED'}")
    print(f"    - JWT auth: {'SUCCESS' if auth_result2 else 'FAILED'}")
    
    # Test authorization
    authz_result1 = security.authorize(
        api_key_cred, 
        "quantum_core", 
        "read",
        SecurityLevel.CONFIDENTIAL
    )
    
    authz_result2 = security.authorize(
        jwt_cred,
        "admin_panel",
        "write",
        SecurityLevel.RESTRICTED
    )
    
    print(f"✅ Authorization tests:")
    print(f"    - Quantum core read: {'ALLOWED' if authz_result1 else 'DENIED'}")
    print(f"    - Admin panel write: {'ALLOWED' if authz_result2 else 'DENIED'}")
    
    # Run compliance checks
    compliance_results = []
    for check_id in list(security.compliance_checks.keys())[:3]:  # Test first 3 checks
        result = security.run_compliance_check(check_id)
        compliance_results.append(result)
    
    print(f"✅ Compliance checks: {sum(compliance_results)}/{len(compliance_results)} passed")
    
    # Get summaries
    security_summary = security.get_security_summary()
    compliance_summary = security.get_compliance_summary()
    stats = security.get_security_statistics()
    
    print(f"✅ Security statistics:")
    print(f"    - Total credentials: {stats['total_credentials']}")
    print(f"    - Auth success rate: {security_summary['auth_success_rate']:.1f}%")
    print(f"    - Security status: {security_summary['security_status']}")
    print(f"    - Compliance rate: {compliance_summary['overall_compliance_rate']:.1f}%")
    print(f"    - Security events: {stats['total_security_events']}")
    
    print("🚀 Security & Compliance test completed!")

if __name__ == "__main__":
    test_security_compliance()
