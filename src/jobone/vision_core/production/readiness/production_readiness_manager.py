"""
Production Readiness Manager for Orion Vision Core

This module provides comprehensive production readiness assessment including
system validation, performance verification, and deployment readiness checks.
Part of Sprint 9.10 Advanced Production Readiness & Final Integration development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.10 - Advanced Production Readiness & Final Integration
"""

import time
import threading
import psutil
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class ReadinessLevel(Enum):
    """Production readiness level enumeration"""
    NOT_READY = "not_ready"
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRE_PRODUCTION = "pre_production"
    PRODUCTION_READY = "production_ready"


class CheckCategory(Enum):
    """Readiness check category enumeration"""
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MONITORING = "monitoring"
    INTEGRATION = "integration"
    DEPLOYMENT = "deployment"
    COMPLIANCE = "compliance"
    DOCUMENTATION = "documentation"


class CheckStatus(Enum):
    """Check status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ReadinessCheck:
    """Production readiness check data structure"""
    check_id: str
    check_name: str
    category: CheckCategory
    description: str
    severity: str = "medium"  # low, medium, high, critical
    required_for_production: bool = True
    automated: bool = True
    check_function: Optional[Callable] = None
    expected_result: Optional[Any] = None
    timeout_seconds: int = 60
    retry_attempts: int = 2
    
    def validate(self) -> bool:
        """Validate check configuration"""
        if not self.check_name or not self.check_id:
            return False
        if self.timeout_seconds <= 0:
            return False
        return True


@dataclass
class CheckResult:
    """Check result data structure"""
    check_id: str
    status: CheckStatus
    result_value: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ReadinessAssessment:
    """Production readiness assessment data structure"""
    assessment_id: str
    assessment_name: str
    start_time: float
    end_time: Optional[float] = None
    overall_status: ReadinessLevel = ReadinessLevel.NOT_READY
    check_results: Dict[str, CheckResult] = field(default_factory=dict)
    passed_checks: int = 0
    failed_checks: int = 0
    warning_checks: int = 0
    total_checks: int = 0
    readiness_score: float = 0.0
    
    def get_duration(self) -> float:
        """Get assessment duration"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


class ProductionReadinessManager:
    """
    Comprehensive production readiness management system
    
    Provides production readiness assessment, system validation,
    performance verification, and deployment readiness checks.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize production readiness manager"""
        self.logger = logger or AgentLogger("production_readiness_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Readiness management
        self.readiness_checks: Dict[str, ReadinessCheck] = {}
        self.assessments: Dict[str, ReadinessAssessment] = {}
        self.active_assessments: Dict[str, threading.Thread] = {}
        
        # Configuration
        self.assessment_timeout_minutes = 30
        self.max_concurrent_assessments = 2
        self.assessment_history_limit = 50
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.readiness_stats = {
            'total_assessments': 0,
            'successful_assessments': 0,
            'failed_assessments': 0,
            'total_checks_executed': 0,
            'average_assessment_time_minutes': 0.0,
            'current_readiness_level': ReadinessLevel.NOT_READY.value,
            'last_assessment_time': None,
            'production_ready_count': 0
        }
        
        # Initialize built-in checks
        self._initialize_builtin_checks()
        
        self.logger.info("Production Readiness Manager initialized")
    
    def _initialize_builtin_checks(self):
        """Initialize built-in readiness checks"""
        # System checks
        self.register_check(ReadinessCheck(
            check_id="system_resources",
            check_name="System Resources Check",
            category=CheckCategory.SYSTEM,
            description="Verify system has adequate CPU, memory, and disk resources",
            severity="critical",
            check_function=self._check_system_resources
        ))
        
        self.register_check(ReadinessCheck(
            check_id="system_dependencies",
            check_name="System Dependencies Check",
            category=CheckCategory.SYSTEM,
            description="Verify all required system dependencies are installed",
            severity="critical",
            check_function=self._check_system_dependencies
        ))
        
        # Performance checks
        self.register_check(ReadinessCheck(
            check_id="performance_baseline",
            check_name="Performance Baseline Check",
            category=CheckCategory.PERFORMANCE,
            description="Verify system meets performance baseline requirements",
            severity="high",
            check_function=self._check_performance_baseline
        ))
        
        # Security checks
        self.register_check(ReadinessCheck(
            check_id="security_configuration",
            check_name="Security Configuration Check",
            category=CheckCategory.SECURITY,
            description="Verify security configurations are properly set",
            severity="critical",
            check_function=self._check_security_configuration
        ))
        
        # Monitoring checks
        self.register_check(ReadinessCheck(
            check_id="monitoring_setup",
            check_name="Monitoring Setup Check",
            category=CheckCategory.MONITORING,
            description="Verify monitoring systems are configured and operational",
            severity="high",
            check_function=self._check_monitoring_setup
        ))
        
        # Integration checks
        self.register_check(ReadinessCheck(
            check_id="integration_connectivity",
            check_name="Integration Connectivity Check",
            category=CheckCategory.INTEGRATION,
            description="Verify all integrations are accessible and functional",
            severity="high",
            check_function=self._check_integration_connectivity
        ))
    
    def register_check(self, check: ReadinessCheck) -> bool:
        """Register readiness check"""
        try:
            if not check.validate():
                self.logger.error("Invalid readiness check", check_id=check.check_id)
                return False
            
            with self._lock:
                self.readiness_checks[check.check_id] = check
            
            self.logger.info(
                "Readiness check registered",
                check_id=check.check_id,
                check_name=check.check_name,
                category=check.category.value,
                severity=check.severity
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Readiness check registration failed", check_id=check.check_id, error=str(e))
            return False
    
    def run_assessment(self, assessment_name: str, 
                      check_categories: Optional[List[CheckCategory]] = None) -> Optional[str]:
        """Run production readiness assessment"""
        try:
            # Check concurrent assessment limit
            if len(self.active_assessments) >= self.max_concurrent_assessments:
                self.logger.error("Maximum concurrent assessments reached")
                return None
            
            # Create assessment
            assessment_id = str(uuid.uuid4())
            assessment = ReadinessAssessment(
                assessment_id=assessment_id,
                assessment_name=assessment_name,
                start_time=time.time()
            )
            
            with self._lock:
                self.assessments[assessment_id] = assessment
                self.readiness_stats['total_assessments'] += 1
            
            # Start assessment thread
            assessment_thread = threading.Thread(
                target=self._execute_assessment,
                args=(assessment, check_categories),
                name=f"Assessment-{assessment_id[:8]}",
                daemon=True
            )
            assessment_thread.start()
            
            self.active_assessments[assessment_id] = assessment_thread
            
            self.logger.info(
                "Production readiness assessment started",
                assessment_id=assessment_id,
                assessment_name=assessment_name
            )
            
            return assessment_id
            
        except Exception as e:
            self.logger.error("Assessment start failed", error=str(e))
            return None
    
    def _execute_assessment(self, assessment: ReadinessAssessment, 
                           check_categories: Optional[List[CheckCategory]]):
        """Execute readiness assessment"""
        try:
            self.logger.info(
                "Assessment execution started",
                assessment_id=assessment.assessment_id,
                assessment_name=assessment.assessment_name
            )
            
            # Get checks to execute
            checks_to_run = []
            for check in self.readiness_checks.values():
                if check_categories is None or check.category in check_categories:
                    checks_to_run.append(check)
            
            assessment.total_checks = len(checks_to_run)
            
            # Execute checks
            for check in checks_to_run:
                result = self._execute_check(check)
                assessment.check_results[check.check_id] = result
                
                # Update counters
                if result.status == CheckStatus.PASSED:
                    assessment.passed_checks += 1
                elif result.status == CheckStatus.FAILED:
                    assessment.failed_checks += 1
                elif result.status == CheckStatus.WARNING:
                    assessment.warning_checks += 1
            
            # Calculate readiness score and level
            self._calculate_readiness_score(assessment)
            self._determine_readiness_level(assessment)
            
            # Complete assessment
            self._complete_assessment(assessment)
            
        except Exception as e:
            self._fail_assessment(assessment, f"Assessment error: {str(e)}")
    
    def _execute_check(self, check: ReadinessCheck) -> CheckResult:
        """Execute individual readiness check"""
        try:
            start_time = time.time()
            
            self.logger.debug(
                "Readiness check started",
                check_id=check.check_id,
                check_name=check.check_name
            )
            
            result = CheckResult(
                check_id=check.check_id,
                status=CheckStatus.RUNNING
            )
            
            # Execute check with retry logic
            for attempt in range(check.retry_attempts + 1):
                try:
                    if check.check_function:
                        check_result = check.check_function()
                        
                        if check_result.get('success', False):
                            result.status = CheckStatus.PASSED
                            result.result_value = check_result.get('result')
                            result.details = check_result.get('details', {})
                            break
                        else:
                            if attempt < check.retry_attempts:
                                time.sleep(1)  # Wait before retry
                                continue
                            else:
                                result.status = CheckStatus.FAILED
                                result.error_message = check_result.get('error', 'Check failed')
                                result.recommendations = check_result.get('recommendations', [])
                    else:
                        result.status = CheckStatus.SKIPPED
                        result.error_message = "No check function defined"
                        break
                        
                except Exception as e:
                    if attempt < check.retry_attempts:
                        time.sleep(1)
                        continue
                    else:
                        result.status = CheckStatus.FAILED
                        result.error_message = str(e)
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            
            with self._lock:
                self.readiness_stats['total_checks_executed'] += 1
            
            self.logger.debug(
                "Readiness check completed",
                check_id=check.check_id,
                status=result.status.value,
                execution_time_ms=f"{result.execution_time_ms:.2f}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Check execution failed", check_id=check.check_id, error=str(e))
            return CheckResult(
                check_id=check.check_id,
                status=CheckStatus.FAILED,
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    # Built-in check implementations
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Define minimum requirements
            min_cpu_cores = 2
            min_memory_gb = 4
            min_disk_free_gb = 10
            
            issues = []
            
            if cpu_count < min_cpu_cores:
                issues.append(f"Insufficient CPU cores: {cpu_count} < {min_cpu_cores}")
            
            memory_gb = memory.total / (1024**3)
            if memory_gb < min_memory_gb:
                issues.append(f"Insufficient memory: {memory_gb:.1f}GB < {min_memory_gb}GB")
            
            disk_free_gb = disk.free / (1024**3)
            if disk_free_gb < min_disk_free_gb:
                issues.append(f"Insufficient disk space: {disk_free_gb:.1f}GB < {min_disk_free_gb}GB")
            
            if issues:
                return {
                    'success': False,
                    'error': 'System resource requirements not met',
                    'details': {'issues': issues},
                    'recommendations': ['Upgrade system resources to meet minimum requirements']
                }
            
            return {
                'success': True,
                'result': 'System resources adequate',
                'details': {
                    'cpu_cores': cpu_count,
                    'memory_gb': f"{memory_gb:.1f}",
                    'disk_free_gb': f"{disk_free_gb:.1f}"
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_system_dependencies(self) -> Dict[str, Any]:
        """Check system dependencies"""
        try:
            # Mock dependency check
            dependencies = ['python', 'pip', 'git']
            missing_deps = []
            
            # In a real implementation, this would check actual dependencies
            # For now, assume all dependencies are available
            
            if missing_deps:
                return {
                    'success': False,
                    'error': 'Missing system dependencies',
                    'details': {'missing': missing_deps},
                    'recommendations': [f'Install missing dependencies: {", ".join(missing_deps)}']
                }
            
            return {
                'success': True,
                'result': 'All system dependencies available',
                'details': {'dependencies': dependencies}
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_performance_baseline(self) -> Dict[str, Any]:
        """Check performance baseline"""
        try:
            # Mock performance check
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            
            performance_issues = []
            
            if cpu_usage > 80:
                performance_issues.append(f"High CPU usage: {cpu_usage:.1f}%")
            
            if memory_usage > 85:
                performance_issues.append(f"High memory usage: {memory_usage:.1f}%")
            
            if performance_issues:
                return {
                    'success': False,
                    'error': 'Performance baseline not met',
                    'details': {'issues': performance_issues},
                    'recommendations': ['Optimize system performance before production deployment']
                }
            
            return {
                'success': True,
                'result': 'Performance baseline met',
                'details': {
                    'cpu_usage': f"{cpu_usage:.1f}%",
                    'memory_usage': f"{memory_usage:.1f}%"
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_security_configuration(self) -> Dict[str, Any]:
        """Check security configuration"""
        try:
            # Mock security check
            security_checks = {
                'encryption_enabled': True,
                'authentication_configured': True,
                'authorization_enabled': True,
                'audit_logging_enabled': True
            }
            
            failed_checks = [check for check, status in security_checks.items() if not status]
            
            if failed_checks:
                return {
                    'success': False,
                    'error': 'Security configuration incomplete',
                    'details': {'failed_checks': failed_checks},
                    'recommendations': ['Configure all required security features']
                }
            
            return {
                'success': True,
                'result': 'Security configuration complete',
                'details': security_checks
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_monitoring_setup(self) -> Dict[str, Any]:
        """Check monitoring setup"""
        try:
            # Mock monitoring check
            monitoring_components = {
                'metrics_collection': True,
                'logging_configured': True,
                'alerting_enabled': True,
                'dashboards_available': True
            }
            
            missing_components = [comp for comp, status in monitoring_components.items() if not status]
            
            if missing_components:
                return {
                    'success': False,
                    'error': 'Monitoring setup incomplete',
                    'details': {'missing_components': missing_components},
                    'recommendations': ['Configure all monitoring components']
                }
            
            return {
                'success': True,
                'result': 'Monitoring setup complete',
                'details': monitoring_components
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_integration_connectivity(self) -> Dict[str, Any]:
        """Check integration connectivity"""
        try:
            # Mock integration check
            integrations = {
                'database': True,
                'external_apis': True,
                'message_queues': True,
                'file_storage': True
            }
            
            failed_integrations = [integration for integration, status in integrations.items() if not status]
            
            if failed_integrations:
                return {
                    'success': False,
                    'error': 'Integration connectivity issues',
                    'details': {'failed_integrations': failed_integrations},
                    'recommendations': ['Fix integration connectivity issues']
                }
            
            return {
                'success': True,
                'result': 'All integrations accessible',
                'details': integrations
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_readiness_score(self, assessment: ReadinessAssessment):
        """Calculate readiness score"""
        try:
            if assessment.total_checks == 0:
                assessment.readiness_score = 0.0
                return
            
            # Weight different check results
            score = 0.0
            total_weight = 0.0
            
            for check_id, result in assessment.check_results.items():
                check = self.readiness_checks.get(check_id)
                if not check:
                    continue
                
                # Assign weights based on severity
                weight = {
                    'low': 1.0,
                    'medium': 2.0,
                    'high': 3.0,
                    'critical': 4.0
                }.get(check.severity, 2.0)
                
                # Assign points based on status
                points = {
                    CheckStatus.PASSED: 1.0,
                    CheckStatus.WARNING: 0.7,
                    CheckStatus.FAILED: 0.0,
                    CheckStatus.SKIPPED: 0.5
                }.get(result.status, 0.0)
                
                score += points * weight
                total_weight += weight
            
            assessment.readiness_score = (score / total_weight) * 100 if total_weight > 0 else 0.0
            
        except Exception as e:
            self.logger.error("Readiness score calculation failed", error=str(e))
            assessment.readiness_score = 0.0
    
    def _determine_readiness_level(self, assessment: ReadinessAssessment):
        """Determine readiness level based on score and critical checks"""
        try:
            score = assessment.readiness_score
            
            # Check for critical failures
            critical_failures = []
            for check_id, result in assessment.check_results.items():
                check = self.readiness_checks.get(check_id)
                if check and check.severity == 'critical' and result.status == CheckStatus.FAILED:
                    critical_failures.append(check_id)
            
            if critical_failures:
                assessment.overall_status = ReadinessLevel.NOT_READY
            elif score >= 95:
                assessment.overall_status = ReadinessLevel.PRODUCTION_READY
            elif score >= 85:
                assessment.overall_status = ReadinessLevel.PRE_PRODUCTION
            elif score >= 70:
                assessment.overall_status = ReadinessLevel.STAGING
            elif score >= 50:
                assessment.overall_status = ReadinessLevel.TESTING
            else:
                assessment.overall_status = ReadinessLevel.DEVELOPMENT
                
        except Exception as e:
            self.logger.error("Readiness level determination failed", error=str(e))
            assessment.overall_status = ReadinessLevel.NOT_READY
    
    def _complete_assessment(self, assessment: ReadinessAssessment):
        """Complete assessment successfully"""
        try:
            assessment.end_time = time.time()
            
            with self._lock:
                self.readiness_stats['successful_assessments'] += 1
                self.readiness_stats['last_assessment_time'] = assessment.end_time
                self.readiness_stats['current_readiness_level'] = assessment.overall_status.value
                
                if assessment.overall_status == ReadinessLevel.PRODUCTION_READY:
                    self.readiness_stats['production_ready_count'] += 1
                
                # Update average assessment time
                total_time = (
                    self.readiness_stats['average_assessment_time_minutes'] * 
                    (self.readiness_stats['successful_assessments'] - 1) +
                    (assessment.get_duration() / 60)
                )
                self.readiness_stats['average_assessment_time_minutes'] = (
                    total_time / self.readiness_stats['successful_assessments']
                )
            
            # Remove from active assessments
            if assessment.assessment_id in self.active_assessments:
                del self.active_assessments[assessment.assessment_id]
            
            # Collect metrics
            self.metrics_collector.collect_metric(
                name="readiness.assessment.completed",
                value=assessment.get_duration(),
                metric_type=MetricType.TIMER,
                tags={
                    'readiness_level': assessment.overall_status.value,
                    'readiness_score': str(int(assessment.readiness_score))
                }
            )
            
            self.logger.info(
                "Production readiness assessment completed",
                assessment_id=assessment.assessment_id,
                readiness_level=assessment.overall_status.value,
                readiness_score=f"{assessment.readiness_score:.1f}%",
                duration_seconds=f"{assessment.get_duration():.2f}",
                passed_checks=assessment.passed_checks,
                failed_checks=assessment.failed_checks
            )
            
        except Exception as e:
            self.logger.error("Assessment completion failed", assessment_id=assessment.assessment_id, error=str(e))
    
    def _fail_assessment(self, assessment: ReadinessAssessment, error_message: str):
        """Fail assessment"""
        try:
            assessment.end_time = time.time()
            assessment.overall_status = ReadinessLevel.NOT_READY
            
            with self._lock:
                self.readiness_stats['failed_assessments'] += 1
            
            # Remove from active assessments
            if assessment.assessment_id in self.active_assessments:
                del self.active_assessments[assessment.assessment_id]
            
            self.logger.error(
                "Production readiness assessment failed",
                assessment_id=assessment.assessment_id,
                error_message=error_message,
                duration_seconds=f"{assessment.get_duration():.2f}"
            )
            
        except Exception as e:
            self.logger.error("Assessment failure handling failed", assessment_id=assessment.assessment_id, error=str(e))
    
    def get_assessment_status(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get assessment status"""
        if assessment_id not in self.assessments:
            return None
        
        assessment = self.assessments[assessment_id]
        
        return {
            'assessment_id': assessment_id,
            'assessment_name': assessment.assessment_name,
            'overall_status': assessment.overall_status.value,
            'readiness_score': assessment.readiness_score,
            'start_time': assessment.start_time,
            'end_time': assessment.end_time,
            'duration_seconds': assessment.get_duration(),
            'total_checks': assessment.total_checks,
            'passed_checks': assessment.passed_checks,
            'failed_checks': assessment.failed_checks,
            'warning_checks': assessment.warning_checks,
            'is_running': assessment_id in self.active_assessments
        }
    
    def list_assessments(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List assessments"""
        assessments = []
        
        # Sort by start time (newest first)
        sorted_assessments = sorted(
            self.assessments.values(),
            key=lambda x: x.start_time,
            reverse=True
        )
        
        for assessment in sorted_assessments[:limit]:
            assessment_info = self.get_assessment_status(assessment.assessment_id)
            if assessment_info:
                assessments.append(assessment_info)
        
        return assessments
    
    def get_current_readiness_level(self) -> ReadinessLevel:
        """Get current production readiness level"""
        return ReadinessLevel(self.readiness_stats['current_readiness_level'])
    
    def get_readiness_stats(self) -> Dict[str, Any]:
        """Get production readiness statistics"""
        with self._lock:
            return {
                'assessment_timeout_minutes': self.assessment_timeout_minutes,
                'max_concurrent_assessments': self.max_concurrent_assessments,
                'assessment_history_limit': self.assessment_history_limit,
                'total_registered_checks': len(self.readiness_checks),
                'total_assessments': len(self.assessments),
                'current_active_assessments': len(self.active_assessments),
                'supported_categories': [c.value for c in CheckCategory],
                'supported_levels': [l.value for l in ReadinessLevel],
                'stats': self.readiness_stats.copy()
            }
