"""
Audit Manager for Orion Vision Core

This module provides comprehensive audit management including
audit logging, trail management, and audit reporting.
Part of Sprint 9.7 Advanced Security & Compliance development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.7 - Advanced Security & Compliance
"""

import time
import threading
import json
import hashlib
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class AuditEventType(Enum):
    """Audit event type enumeration"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CONFIGURATION = "system_configuration"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_CHECK = "compliance_check"
    ADMIN_ACTION = "admin_action"
    API_CALL = "api_call"
    FILE_ACCESS = "file_access"


class AuditSeverity(Enum):
    """Audit severity enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditStatus(Enum):
    """Audit status enumeration"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"
    INVESTIGATED = "investigated"


@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    outcome: str = "success"  # success, failure, partial
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    status: AuditStatus = AuditStatus.ACTIVE
    
    def get_age_hours(self) -> float:
        """Get event age in hours"""
        return (time.time() - self.timestamp) / 3600
    
    def get_hash(self) -> str:
        """Get event hash for integrity verification"""
        event_data = {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'details': self.details
        }
        return hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()


@dataclass
class AuditTrail:
    """Audit trail data structure"""
    trail_id: str
    trail_name: str
    description: str = ""
    event_types: List[AuditEventType] = field(default_factory=list)
    retention_days: int = 365
    encryption_enabled: bool = True
    compression_enabled: bool = True
    events: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_event_at: Optional[float] = None
    
    def validate(self) -> bool:
        """Validate audit trail"""
        if not self.trail_name or not self.trail_id:
            return False
        if self.retention_days <= 0:
            return False
        return True


@dataclass
class AuditReport:
    """Audit report data structure"""
    report_id: str
    report_name: str
    report_type: str  # summary, detailed, compliance, security
    time_range: Dict[str, float] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    events_analyzed: int = 0
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)
    generated_by: Optional[str] = None


class AuditManager:
    """
    Comprehensive audit management system
    
    Provides audit logging, trail management, integrity verification,
    and audit reporting capabilities with compliance support.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize audit manager"""
        self.logger = logger or AgentLogger("audit_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Audit events and trails
        self.audit_events: Dict[str, AuditEvent] = {}
        self.audit_trails: Dict[str, AuditTrail] = {}
        self.audit_reports: Dict[str, AuditReport] = {}
        
        # Event integrity
        self.event_hashes: Dict[str, str] = {}
        self.integrity_checks: Dict[str, bool] = {}
        
        # Configuration
        self.max_events_per_trail = 100000
        self.default_retention_days = 365
        self.auto_archive_enabled = True
        self.integrity_check_interval = 3600  # 1 hour
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.audit_stats = {
            'total_events': 0,
            'events_by_type': {},
            'events_by_severity': {},
            'total_trails': 0,
            'active_trails': 0,
            'total_reports': 0,
            'integrity_checks_passed': 0,
            'integrity_checks_failed': 0,
            'events_archived': 0,
            'storage_size_mb': 0.0
        }
        
        # Initialize default audit trail
        self._initialize_default_trail()
        
        self.logger.info("Audit Manager initialized")
    
    def _initialize_default_trail(self):
        """Initialize default audit trail"""
        default_trail = AuditTrail(
            trail_id="default_trail",
            trail_name="Default Audit Trail",
            description="Default audit trail for all system events",
            event_types=list(AuditEventType),
            retention_days=self.default_retention_days
        )
        self.create_audit_trail(default_trail)
    
    def create_audit_trail(self, trail: AuditTrail) -> bool:
        """Create audit trail"""
        try:
            # Validate trail
            if not trail.validate():
                self.logger.error("Invalid audit trail", trail_id=trail.trail_id)
                return False
            
            with self._lock:
                # Store trail
                self.audit_trails[trail.trail_id] = trail
                
                # Update statistics
                self.audit_stats['total_trails'] = len(self.audit_trails)
                self.audit_stats['active_trails'] = len([
                    t for t in self.audit_trails.values() 
                    if t.retention_days > 0
                ])
            
            self.logger.info(
                "Audit trail created",
                trail_id=trail.trail_id,
                trail_name=trail.trail_name,
                event_types_count=len(trail.event_types),
                retention_days=trail.retention_days
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Audit trail creation failed", trail_id=trail.trail_id, error=str(e))
            return False
    
    def log_audit_event(self, event_type: AuditEventType, severity: AuditSeverity,
                       user_id: Optional[str] = None, session_id: Optional[str] = None,
                       source_ip: Optional[str] = None, resource: Optional[str] = None,
                       action: Optional[str] = None, outcome: str = "success",
                       details: Optional[Dict[str, Any]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log audit event"""
        try:
            event_id = str(uuid.uuid4())
            
            # Create audit event
            event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                session_id=session_id,
                source_ip=source_ip,
                resource=resource,
                action=action,
                outcome=outcome,
                details=details or {},
                metadata=metadata or {}
            )
            
            # Calculate event hash for integrity
            event_hash = event.get_hash()
            
            with self._lock:
                # Store event
                self.audit_events[event_id] = event
                self.event_hashes[event_id] = event_hash
                
                # Add to relevant trails
                for trail in self.audit_trails.values():
                    if event_type in trail.event_types or not trail.event_types:
                        trail.events.append(event_id)
                        trail.last_event_at = time.time()
                        
                        # Check trail size limits
                        if len(trail.events) > self.max_events_per_trail:
                            # Archive oldest events
                            self._archive_trail_events(trail, 1000)
                
                # Update statistics
                self.audit_stats['total_events'] = len(self.audit_events)
                
                event_type_key = event_type.value
                if event_type_key not in self.audit_stats['events_by_type']:
                    self.audit_stats['events_by_type'][event_type_key] = 0
                self.audit_stats['events_by_type'][event_type_key] += 1
                
                severity_key = severity.value
                if severity_key not in self.audit_stats['events_by_severity']:
                    self.audit_stats['events_by_severity'][severity_key] = 0
                self.audit_stats['events_by_severity'][severity_key] += 1
            
            # Collect metrics
            self.metrics_collector.collect_metric(
                name="audit.event_logged",
                value=1,
                metric_type=MetricType.COUNTER,
                tags={
                    'event_type': event_type.value,
                    'severity': severity.value,
                    'outcome': outcome
                }
            )
            
            self.logger.info(
                "Audit event logged",
                event_id=event_id,
                event_type=event_type.value,
                severity=severity.value,
                user_id=user_id,
                resource=resource,
                action=action,
                outcome=outcome
            )
            
            return event_id
            
        except Exception as e:
            self.logger.error("Audit event logging failed", event_type=event_type.value, error=str(e))
            return ""
    
    def verify_event_integrity(self, event_id: str) -> bool:
        """Verify audit event integrity"""
        try:
            if event_id not in self.audit_events:
                return False
            
            event = self.audit_events[event_id]
            stored_hash = self.event_hashes.get(event_id)
            current_hash = event.get_hash()
            
            integrity_valid = stored_hash == current_hash
            
            with self._lock:
                self.integrity_checks[event_id] = integrity_valid
                
                if integrity_valid:
                    self.audit_stats['integrity_checks_passed'] += 1
                else:
                    self.audit_stats['integrity_checks_failed'] += 1
            
            if not integrity_valid:
                self.logger.warning(
                    "Audit event integrity check failed",
                    event_id=event_id,
                    stored_hash=stored_hash,
                    current_hash=current_hash
                )
            
            return integrity_valid
            
        except Exception as e:
            self.logger.error("Event integrity verification failed", event_id=event_id, error=str(e))
            return False
    
    def search_audit_events(self, filters: Dict[str, Any], limit: int = 1000) -> List[Dict[str, Any]]:
        """Search audit events with filters"""
        try:
            matching_events = []
            
            for event in self.audit_events.values():
                # Apply filters
                if 'event_type' in filters and event.event_type.value != filters['event_type']:
                    continue
                if 'severity' in filters and event.severity.value != filters['severity']:
                    continue
                if 'user_id' in filters and event.user_id != filters['user_id']:
                    continue
                if 'source_ip' in filters and event.source_ip != filters['source_ip']:
                    continue
                if 'outcome' in filters and event.outcome != filters['outcome']:
                    continue
                if 'start_time' in filters and event.timestamp < filters['start_time']:
                    continue
                if 'end_time' in filters and event.timestamp > filters['end_time']:
                    continue
                
                # Convert to dict
                event_dict = {
                    'event_id': event.event_id,
                    'event_type': event.event_type.value,
                    'severity': event.severity.value,
                    'user_id': event.user_id,
                    'session_id': event.session_id,
                    'source_ip': event.source_ip,
                    'resource': event.resource,
                    'action': event.action,
                    'outcome': event.outcome,
                    'timestamp': event.timestamp,
                    'age_hours': event.get_age_hours(),
                    'status': event.status.value,
                    'details': event.details,
                    'metadata': event.metadata
                }
                
                matching_events.append(event_dict)
            
            # Sort by timestamp (newest first) and limit
            matching_events.sort(key=lambda x: x['timestamp'], reverse=True)
            
            self.logger.debug(
                "Audit event search completed",
                filters=filters,
                results_count=len(matching_events[:limit])
            )
            
            return matching_events[:limit]
            
        except Exception as e:
            self.logger.error("Audit event search failed", filters=filters, error=str(e))
            return []
    
    def generate_audit_report(self, report_name: str, report_type: str,
                             time_range: Dict[str, float], filters: Optional[Dict[str, Any]] = None,
                             generated_by: Optional[str] = None) -> Optional[str]:
        """Generate audit report"""
        try:
            report_id = str(uuid.uuid4())
            
            # Search events for the report
            search_filters = filters or {}
            search_filters.update(time_range)
            
            events = self.search_audit_events(search_filters, limit=10000)
            
            # Analyze events
            findings = self._analyze_events_for_report(events, report_type)
            recommendations = self._generate_report_recommendations(events, findings, report_type)
            
            # Create report
            report = AuditReport(
                report_id=report_id,
                report_name=report_name,
                report_type=report_type,
                time_range=time_range,
                filters=filters or {},
                events_analyzed=len(events),
                findings=findings,
                recommendations=recommendations,
                generated_by=generated_by
            )
            
            with self._lock:
                self.audit_reports[report_id] = report
                self.audit_stats['total_reports'] = len(self.audit_reports)
            
            self.logger.info(
                "Audit report generated",
                report_id=report_id,
                report_name=report_name,
                report_type=report_type,
                events_analyzed=len(events),
                findings_count=len(findings)
            )
            
            return report_id
            
        except Exception as e:
            self.logger.error("Audit report generation failed", report_name=report_name, error=str(e))
            return None
    
    def _analyze_events_for_report(self, events: List[Dict[str, Any]], report_type: str) -> List[Dict[str, Any]]:
        """Analyze events for report findings"""
        findings = []
        
        if report_type == "security":
            # Security-focused analysis
            failed_logins = [e for e in events if e['event_type'] == 'user_login' and e['outcome'] == 'failure']
            if len(failed_logins) > 10:
                findings.append({
                    'type': 'security_concern',
                    'title': 'High Number of Failed Login Attempts',
                    'description': f'Detected {len(failed_logins)} failed login attempts',
                    'severity': 'high',
                    'count': len(failed_logins)
                })
            
            # Check for suspicious IP addresses
            ip_counts = {}
            for event in events:
                if event['source_ip']:
                    ip_counts[event['source_ip']] = ip_counts.get(event['source_ip'], 0) + 1
            
            suspicious_ips = [ip for ip, count in ip_counts.items() if count > 100]
            if suspicious_ips:
                findings.append({
                    'type': 'security_concern',
                    'title': 'Suspicious IP Activity',
                    'description': f'High activity from IPs: {", ".join(suspicious_ips)}',
                    'severity': 'medium',
                    'ips': suspicious_ips
                })
        
        elif report_type == "compliance":
            # Compliance-focused analysis
            admin_actions = [e for e in events if e['event_type'] == 'admin_action']
            findings.append({
                'type': 'compliance_metric',
                'title': 'Administrative Actions',
                'description': f'Total administrative actions: {len(admin_actions)}',
                'severity': 'info',
                'count': len(admin_actions)
            })
            
            data_access_events = [e for e in events if e['event_type'] == 'data_access']
            findings.append({
                'type': 'compliance_metric',
                'title': 'Data Access Events',
                'description': f'Total data access events: {len(data_access_events)}',
                'severity': 'info',
                'count': len(data_access_events)
            })
        
        elif report_type == "summary":
            # Summary analysis
            event_types = {}
            for event in events:
                event_type = event['event_type']
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            findings.append({
                'type': 'summary',
                'title': 'Event Type Distribution',
                'description': 'Distribution of events by type',
                'severity': 'info',
                'distribution': event_types
            })
        
        return findings
    
    def _generate_report_recommendations(self, events: List[Dict[str, Any]], 
                                       findings: List[Dict[str, Any]], report_type: str) -> List[str]:
        """Generate recommendations based on report findings"""
        recommendations = []
        
        if report_type == "security":
            # Security recommendations
            failed_login_findings = [f for f in findings if 'Failed Login' in f.get('title', '')]
            if failed_login_findings:
                recommendations.append("Implement account lockout policies to prevent brute force attacks")
                recommendations.append("Enable multi-factor authentication for all user accounts")
            
            suspicious_ip_findings = [f for f in findings if 'Suspicious IP' in f.get('title', '')]
            if suspicious_ip_findings:
                recommendations.append("Implement IP-based access controls and monitoring")
                recommendations.append("Review and update firewall rules")
        
        elif report_type == "compliance":
            # Compliance recommendations
            recommendations.extend([
                "Ensure all administrative actions are properly documented",
                "Implement regular access reviews and certifications",
                "Maintain audit logs for the required retention period"
            ])
        
        # General recommendations
        if len(events) > 1000:
            recommendations.append("Consider implementing log aggregation and analysis tools")
        
        return recommendations
    
    def _archive_trail_events(self, trail: AuditTrail, count: int):
        """Archive oldest events from trail"""
        if len(trail.events) <= count:
            return
        
        # Archive oldest events
        events_to_archive = trail.events[:count]
        trail.events = trail.events[count:]
        
        # Mark events as archived
        for event_id in events_to_archive:
            if event_id in self.audit_events:
                self.audit_events[event_id].status = AuditStatus.ARCHIVED
        
        with self._lock:
            self.audit_stats['events_archived'] += len(events_to_archive)
        
        self.logger.info(
            "Trail events archived",
            trail_id=trail.trail_id,
            events_archived=len(events_to_archive)
        )
    
    def get_audit_trail(self, trail_id: str) -> Optional[AuditTrail]:
        """Get audit trail by ID"""
        return self.audit_trails.get(trail_id)
    
    def get_audit_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get audit report by ID"""
        if report_id not in self.audit_reports:
            return None
        
        report = self.audit_reports[report_id]
        
        return {
            'report_id': report.report_id,
            'report_name': report.report_name,
            'report_type': report.report_type,
            'time_range': report.time_range,
            'filters': report.filters,
            'events_analyzed': report.events_analyzed,
            'findings': report.findings,
            'recommendations': report.recommendations,
            'generated_at': report.generated_at,
            'generated_by': report.generated_by
        }
    
    def list_audit_trails(self) -> List[Dict[str, Any]]:
        """List all audit trails"""
        trails = []
        
        for trail in self.audit_trails.values():
            trails.append({
                'trail_id': trail.trail_id,
                'trail_name': trail.trail_name,
                'description': trail.description,
                'event_types_count': len(trail.event_types),
                'events_count': len(trail.events),
                'retention_days': trail.retention_days,
                'encryption_enabled': trail.encryption_enabled,
                'created_at': trail.created_at,
                'last_event_at': trail.last_event_at
            })
        
        return sorted(trails, key=lambda x: x['created_at'], reverse=True)
    
    def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit manager statistics"""
        with self._lock:
            # Calculate storage size (mock)
            storage_size_mb = len(self.audit_events) * 0.001  # Mock calculation
            
            return {
                'total_events': len(self.audit_events),
                'total_trails': len(self.audit_trails),
                'total_reports': len(self.audit_reports),
                'integrity_checks_total': len(self.integrity_checks),
                'max_events_per_trail': self.max_events_per_trail,
                'default_retention_days': self.default_retention_days,
                'auto_archive_enabled': self.auto_archive_enabled,
                'storage_size_mb': storage_size_mb,
                'supported_event_types': [et.value for et in AuditEventType],
                'stats': self.audit_stats.copy()
            }
