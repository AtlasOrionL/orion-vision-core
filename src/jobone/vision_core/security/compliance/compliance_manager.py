"""
Compliance Manager for Orion Vision Core

This module provides comprehensive compliance management including
regulatory compliance, policy enforcement, and compliance reporting.
Part of Sprint 9.7 Advanced Security & Compliance development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.7 - Advanced Security & Compliance
"""

import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class ComplianceFramework(Enum):
    """Compliance framework enumeration"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    NIST = "nist"
    SOC2 = "soc2"
    CCPA = "ccpa"


class ComplianceStatus(Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    REMEDIATION_REQUIRED = "remediation_required"


class ViolationSeverity(Enum):
    """Violation severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceRule:
    """Compliance rule data structure"""
    rule_id: str
    rule_name: str
    framework: ComplianceFramework
    description: str
    requirements: List[str] = field(default_factory=list)
    validation_criteria: Dict[str, Any] = field(default_factory=dict)
    remediation_steps: List[str] = field(default_factory=list)
    mandatory: bool = True
    created_at: float = field(default_factory=time.time)
    
    def validate(self) -> bool:
        """Validate compliance rule"""
        if not self.rule_name or not self.rule_id:
            return False
        if not self.requirements:
            return False
        return True


@dataclass
class ComplianceViolation:
    """Compliance violation data structure"""
    violation_id: str
    rule_id: str
    severity: ViolationSeverity
    description: str
    affected_resource: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    remediation_status: str = "open"  # open, in_progress, resolved, accepted_risk
    assigned_to: Optional[str] = None
    due_date: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    
    def get_age_days(self) -> float:
        """Get violation age in days"""
        return (time.time() - self.created_at) / (24 * 3600)
    
    def is_overdue(self) -> bool:
        """Check if violation is overdue"""
        if not self.due_date:
            return False
        return time.time() > self.due_date and self.remediation_status == "open"


@dataclass
class ComplianceAssessment:
    """Compliance assessment data structure"""
    assessment_id: str
    assessment_name: str
    framework: ComplianceFramework
    scope: List[str] = field(default_factory=list)
    status: ComplianceStatus = ComplianceStatus.UNDER_REVIEW
    overall_score: float = 0.0
    rules_evaluated: int = 0
    rules_passed: int = 0
    rules_failed: int = 0
    violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessor: Optional[str] = None
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    
    def get_compliance_percentage(self) -> float:
        """Get compliance percentage"""
        if self.rules_evaluated == 0:
            return 0.0
        return (self.rules_passed / self.rules_evaluated) * 100


class ComplianceManager:
    """
    Comprehensive compliance management system
    
    Provides regulatory compliance monitoring, policy enforcement,
    violation tracking, and compliance reporting capabilities.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize compliance manager"""
        self.logger = logger or AgentLogger("compliance_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Compliance rules and violations
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.compliance_violations: Dict[str, ComplianceViolation] = {}
        self.compliance_assessments: Dict[str, ComplianceAssessment] = {}
        
        # Framework configurations
        self.framework_configs: Dict[ComplianceFramework, Dict[str, Any]] = {}
        
        # Monitoring and enforcement
        self.active_monitors: Dict[str, Dict[str, Any]] = {}
        self.enforcement_actions: Dict[str, List[str]] = {}
        
        # Configuration
        self.auto_remediation_enabled = True
        self.violation_retention_days = 365
        self.assessment_frequency_days = 90
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.compliance_stats = {
            'total_rules': 0,
            'active_rules': 0,
            'total_violations': 0,
            'open_violations': 0,
            'critical_violations': 0,
            'resolved_violations': 0,
            'total_assessments': 0,
            'compliant_assessments': 0,
            'average_compliance_score': 0.0,
            'overdue_violations': 0
        }
        
        # Initialize default compliance rules
        self._initialize_default_rules()
        
        self.logger.info("Compliance Manager initialized")
    
    def _initialize_default_rules(self):
        """Initialize default compliance rules"""
        # GDPR data protection rule
        gdpr_rule = ComplianceRule(
            rule_id="gdpr_data_protection",
            rule_name="GDPR Data Protection Requirements",
            framework=ComplianceFramework.GDPR,
            description="Ensure personal data is processed lawfully and securely",
            requirements=[
                "Implement data encryption at rest and in transit",
                "Maintain data processing records",
                "Implement right to be forgotten",
                "Conduct privacy impact assessments"
            ],
            validation_criteria={
                "encryption_enabled": True,
                "data_retention_policy": True,
                "consent_management": True
            }
        )
        self.create_compliance_rule(gdpr_rule)
        
        # ISO 27001 access control rule
        iso_rule = ComplianceRule(
            rule_id="iso27001_access_control",
            rule_name="ISO 27001 Access Control",
            framework=ComplianceFramework.ISO_27001,
            description="Implement proper access control mechanisms",
            requirements=[
                "Role-based access control",
                "Regular access reviews",
                "Strong authentication",
                "Privileged access management"
            ],
            validation_criteria={
                "rbac_enabled": True,
                "mfa_required": True,
                "access_review_frequency": 90
            }
        )
        self.create_compliance_rule(iso_rule)
    
    def create_compliance_rule(self, rule: ComplianceRule) -> bool:
        """Create compliance rule"""
        try:
            # Validate rule
            if not rule.validate():
                self.logger.error("Invalid compliance rule", rule_id=rule.rule_id)
                return False
            
            with self._lock:
                # Store rule
                self.compliance_rules[rule.rule_id] = rule
                
                # Update statistics
                self.compliance_stats['total_rules'] = len(self.compliance_rules)
                self.compliance_stats['active_rules'] = len(self.compliance_rules)
            
            self.logger.info(
                "Compliance rule created",
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                framework=rule.framework.value,
                requirements_count=len(rule.requirements)
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Compliance rule creation failed", rule_id=rule.rule_id, error=str(e))
            return False
    
    def evaluate_compliance(self, rule_id: str, system_state: Dict[str, Any]) -> bool:
        """Evaluate compliance against a specific rule"""
        try:
            if rule_id not in self.compliance_rules:
                self.logger.error("Compliance rule not found", rule_id=rule_id)
                return False
            
            rule = self.compliance_rules[rule_id]
            
            # Evaluate validation criteria
            compliance_passed = True
            failed_criteria = []
            
            for criterion, expected_value in rule.validation_criteria.items():
                actual_value = system_state.get(criterion)
                
                if isinstance(expected_value, bool):
                    if actual_value != expected_value:
                        compliance_passed = False
                        failed_criteria.append(criterion)
                elif isinstance(expected_value, (int, float)):
                    if actual_value is None or actual_value < expected_value:
                        compliance_passed = False
                        failed_criteria.append(criterion)
                else:
                    if actual_value != expected_value:
                        compliance_passed = False
                        failed_criteria.append(criterion)
            
            if not compliance_passed:
                # Create violation
                self._create_violation(rule, failed_criteria, system_state)
            
            self.logger.debug(
                "Compliance evaluation completed",
                rule_id=rule_id,
                compliance_passed=compliance_passed,
                failed_criteria=failed_criteria
            )
            
            return compliance_passed
            
        except Exception as e:
            self.logger.error("Compliance evaluation failed", rule_id=rule_id, error=str(e))
            return False
    
    def _create_violation(self, rule: ComplianceRule, failed_criteria: List[str], 
                         system_state: Dict[str, Any]):
        """Create compliance violation"""
        violation_id = str(uuid.uuid4())
        
        # Determine severity based on rule and failed criteria
        severity = ViolationSeverity.MEDIUM
        if rule.mandatory and len(failed_criteria) > 2:
            severity = ViolationSeverity.HIGH
        if rule.framework in [ComplianceFramework.GDPR, ComplianceFramework.HIPAA]:
            severity = ViolationSeverity.HIGH
        
        violation = ComplianceViolation(
            violation_id=violation_id,
            rule_id=rule.rule_id,
            severity=severity,
            description=f"Compliance violation for {rule.rule_name}: {', '.join(failed_criteria)}",
            evidence={
                "failed_criteria": failed_criteria,
                "system_state": system_state,
                "rule_framework": rule.framework.value
            },
            due_date=time.time() + (30 * 24 * 3600)  # 30 days from now
        )
        
        with self._lock:
            self.compliance_violations[violation_id] = violation
            
            # Update statistics
            self.compliance_stats['total_violations'] = len(self.compliance_violations)
            self.compliance_stats['open_violations'] = len([
                v for v in self.compliance_violations.values() 
                if v.remediation_status == "open"
            ])
            
            if severity == ViolationSeverity.CRITICAL:
                self.compliance_stats['critical_violations'] += 1
        
        # Collect metrics
        self.metrics_collector.collect_metric(
            name="compliance.violation_created",
            value=1,
            metric_type=MetricType.COUNTER,
            tags={
                'rule_id': rule.rule_id,
                'framework': rule.framework.value,
                'severity': severity.value
            }
        )
        
        self.logger.warning(
            "Compliance violation created",
            violation_id=violation_id,
            rule_id=rule.rule_id,
            severity=severity.value,
            failed_criteria=failed_criteria
        )
        
        # Trigger auto-remediation if enabled
        if self.auto_remediation_enabled:
            self._attempt_auto_remediation(violation)
    
    def _attempt_auto_remediation(self, violation: ComplianceViolation):
        """Attempt automatic remediation of violation"""
        try:
            rule = self.compliance_rules.get(violation.rule_id)
            if not rule or not rule.remediation_steps:
                return
            
            # Mock auto-remediation
            auto_remediation_success = len(rule.remediation_steps) <= 3  # Simple heuristic
            
            if auto_remediation_success:
                violation.remediation_status = "resolved"
                violation.resolved_at = time.time()
                
                with self._lock:
                    self.compliance_stats['resolved_violations'] += 1
                    self.compliance_stats['open_violations'] -= 1
                
                self.logger.info(
                    "Auto-remediation successful",
                    violation_id=violation.violation_id,
                    rule_id=violation.rule_id
                )
            else:
                violation.remediation_status = "in_progress"
                
                self.logger.info(
                    "Auto-remediation initiated",
                    violation_id=violation.violation_id,
                    rule_id=violation.rule_id
                )
                
        except Exception as e:
            self.logger.error("Auto-remediation failed", violation_id=violation.violation_id, error=str(e))
    
    def conduct_assessment(self, assessment_name: str, framework: ComplianceFramework,
                          scope: List[str], system_state: Dict[str, Any]) -> Optional[str]:
        """Conduct compliance assessment"""
        try:
            assessment_id = str(uuid.uuid4())
            
            assessment = ComplianceAssessment(
                assessment_id=assessment_id,
                assessment_name=assessment_name,
                framework=framework,
                scope=scope
            )
            
            # Evaluate relevant rules
            framework_rules = [
                rule for rule in self.compliance_rules.values()
                if rule.framework == framework
            ]
            
            rules_passed = 0
            rules_failed = 0
            violations = []
            
            for rule in framework_rules:
                if self.evaluate_compliance(rule.rule_id, system_state):
                    rules_passed += 1
                else:
                    rules_failed += 1
                    # Find recent violations for this rule
                    rule_violations = [
                        v.violation_id for v in self.compliance_violations.values()
                        if v.rule_id == rule.rule_id and v.get_age_days() <= 1
                    ]
                    violations.extend(rule_violations)
            
            # Update assessment results
            assessment.rules_evaluated = len(framework_rules)
            assessment.rules_passed = rules_passed
            assessment.rules_failed = rules_failed
            assessment.violations = violations
            assessment.overall_score = assessment.get_compliance_percentage()
            assessment.completed_at = time.time()
            
            # Determine status
            if assessment.overall_score >= 95:
                assessment.status = ComplianceStatus.COMPLIANT
            elif assessment.overall_score >= 80:
                assessment.status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                assessment.status = ComplianceStatus.NON_COMPLIANT
            
            # Generate recommendations
            assessment.recommendations = self._generate_recommendations(assessment, framework_rules)
            
            with self._lock:
                self.compliance_assessments[assessment_id] = assessment
                
                # Update statistics
                self.compliance_stats['total_assessments'] = len(self.compliance_assessments)
                if assessment.status == ComplianceStatus.COMPLIANT:
                    self.compliance_stats['compliant_assessments'] += 1
                
                # Calculate average compliance score
                total_score = sum(a.overall_score for a in self.compliance_assessments.values())
                self.compliance_stats['average_compliance_score'] = (
                    total_score / len(self.compliance_assessments)
                )
            
            self.logger.info(
                "Compliance assessment completed",
                assessment_id=assessment_id,
                assessment_name=assessment_name,
                framework=framework.value,
                overall_score=f"{assessment.overall_score:.1f}%",
                status=assessment.status.value,
                rules_evaluated=assessment.rules_evaluated
            )
            
            return assessment_id
            
        except Exception as e:
            self.logger.error("Compliance assessment failed", assessment_name=assessment_name, error=str(e))
            return None
    
    def _generate_recommendations(self, assessment: ComplianceAssessment, 
                                 rules: List[ComplianceRule]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if assessment.overall_score < 80:
            recommendations.append("Immediate attention required for critical compliance gaps")
        
        if assessment.rules_failed > 0:
            recommendations.append(f"Address {assessment.rules_failed} failed compliance rules")
        
        # Framework-specific recommendations
        if assessment.framework == ComplianceFramework.GDPR:
            recommendations.extend([
                "Review data processing activities and consent mechanisms",
                "Implement privacy by design principles",
                "Conduct regular data protection impact assessments"
            ])
        elif assessment.framework == ComplianceFramework.ISO_27001:
            recommendations.extend([
                "Strengthen access control mechanisms",
                "Implement continuous security monitoring",
                "Conduct regular security awareness training"
            ])
        
        return recommendations
    
    def resolve_violation(self, violation_id: str, resolution_notes: str) -> bool:
        """Resolve compliance violation"""
        try:
            if violation_id not in self.compliance_violations:
                self.logger.error("Violation not found", violation_id=violation_id)
                return False
            
            violation = self.compliance_violations[violation_id]
            violation.remediation_status = "resolved"
            violation.resolved_at = time.time()
            
            with self._lock:
                self.compliance_stats['resolved_violations'] += 1
                self.compliance_stats['open_violations'] -= 1
            
            self.logger.info(
                "Compliance violation resolved",
                violation_id=violation_id,
                rule_id=violation.rule_id,
                resolution_notes=resolution_notes
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Violation resolution failed", violation_id=violation_id, error=str(e))
            return False
    
    def get_compliance_violations(self, severity_filter: Optional[ViolationSeverity] = None,
                                 status_filter: Optional[str] = None,
                                 limit: int = 100) -> List[Dict[str, Any]]:
        """Get compliance violations with optional filtering"""
        violations = []
        
        for violation in self.compliance_violations.values():
            if severity_filter and violation.severity != severity_filter:
                continue
            if status_filter and violation.remediation_status != status_filter:
                continue
            
            violations.append({
                'violation_id': violation.violation_id,
                'rule_id': violation.rule_id,
                'severity': violation.severity.value,
                'description': violation.description,
                'affected_resource': violation.affected_resource,
                'remediation_status': violation.remediation_status,
                'assigned_to': violation.assigned_to,
                'age_days': violation.get_age_days(),
                'is_overdue': violation.is_overdue(),
                'created_at': violation.created_at,
                'resolved_at': violation.resolved_at
            })
        
        # Sort by creation time (newest first) and limit
        violations.sort(key=lambda x: x['created_at'], reverse=True)
        return violations[:limit]
    
    def get_assessment_results(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get compliance assessment results"""
        if assessment_id not in self.compliance_assessments:
            return None
        
        assessment = self.compliance_assessments[assessment_id]
        
        return {
            'assessment_id': assessment.assessment_id,
            'assessment_name': assessment.assessment_name,
            'framework': assessment.framework.value,
            'scope': assessment.scope,
            'status': assessment.status.value,
            'overall_score': assessment.overall_score,
            'compliance_percentage': assessment.get_compliance_percentage(),
            'rules_evaluated': assessment.rules_evaluated,
            'rules_passed': assessment.rules_passed,
            'rules_failed': assessment.rules_failed,
            'violations_count': len(assessment.violations),
            'recommendations': assessment.recommendations,
            'started_at': assessment.started_at,
            'completed_at': assessment.completed_at
        }
    
    def list_compliance_rules(self, framework_filter: Optional[ComplianceFramework] = None) -> List[Dict[str, Any]]:
        """List compliance rules with optional framework filtering"""
        rules = []
        
        for rule in self.compliance_rules.values():
            if framework_filter and rule.framework != framework_filter:
                continue
            
            rules.append({
                'rule_id': rule.rule_id,
                'rule_name': rule.rule_name,
                'framework': rule.framework.value,
                'description': rule.description,
                'requirements_count': len(rule.requirements),
                'mandatory': rule.mandatory,
                'created_at': rule.created_at
            })
        
        return sorted(rules, key=lambda x: x['created_at'], reverse=True)
    
    def get_compliance_stats(self) -> Dict[str, Any]:
        """Get compliance manager statistics"""
        with self._lock:
            # Calculate overdue violations
            overdue_violations = len([
                v for v in self.compliance_violations.values() if v.is_overdue()
            ])
            
            return {
                'total_rules': len(self.compliance_rules),
                'total_violations': len(self.compliance_violations),
                'total_assessments': len(self.compliance_assessments),
                'supported_frameworks': [f.value for f in ComplianceFramework],
                'auto_remediation_enabled': self.auto_remediation_enabled,
                'violation_retention_days': self.violation_retention_days,
                'assessment_frequency_days': self.assessment_frequency_days,
                'overdue_violations': overdue_violations,
                'stats': self.compliance_stats.copy()
            }
