"""
Security Module Exports

This module exports all security classes and utilities.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
"""

# Authentication classes
from .auth import (
    AuthenticationManager,
    User,
    Session,
    AuthMethod,
    UserRole,
    SessionStatus
)

# Encryption classes
from .encryption import (
    EncryptionManager,
    EncryptionKey,
    EncryptedData,
    EncryptionAlgorithm,
    HashAlgorithm
)

# Core security classes (Sprint 9.7)
from .core import (
    SecurityManager,
    SecurityPolicy,
    SecurityEvent,
    AccessToken,
    SecurityLevel,
    ThreatLevel
)

# Compliance classes (Sprint 9.7)
from .compliance import (
    ComplianceManager,
    ComplianceRule,
    ComplianceViolation,
    ComplianceAssessment,
    ComplianceFramework,
    ComplianceStatus,
    ViolationSeverity
)

# Audit classes (Sprint 9.7)
from .audit import (
    AuditManager,
    AuditEvent,
    AuditTrail,
    AuditReport,
    AuditEventType,
    AuditSeverity,
    AuditStatus
)

__all__ = [
    # Authentication
    'AuthenticationManager',
    'User',
    'Session',
    'AuthMethod',
    'UserRole',
    'SessionStatus',

    # Encryption
    'EncryptionManager',
    'EncryptionKey',
    'EncryptedData',
    'EncryptionAlgorithm',
    'HashAlgorithm',

    # Core Security (Sprint 9.7)
    'SecurityManager',
    'SecurityPolicy',
    'SecurityEvent',
    'AccessToken',
    'SecurityLevel',
    'ThreatLevel',

    # Compliance (Sprint 9.7)
    'ComplianceManager',
    'ComplianceRule',
    'ComplianceViolation',
    'ComplianceAssessment',
    'ComplianceFramework',
    'ComplianceStatus',
    'ViolationSeverity',

    # Audit (Sprint 9.7)
    'AuditManager',
    'AuditEvent',
    'AuditTrail',
    'AuditReport',
    'AuditEventType',
    'AuditSeverity',
    'AuditStatus'
]

__version__ = "9.7.0"
__author__ = "Atlas-orion (Augment Agent)"
__sprint__ = "9.7 - Advanced Security & Compliance"
