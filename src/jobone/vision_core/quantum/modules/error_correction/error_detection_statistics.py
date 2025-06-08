"""
🔍 Error Detection Statistics - Q05.2.2 Statistics Component

Statistics and analysis for Error Detection systems
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q05.2.2 Quantum Error Detection
Priority: CRITICAL - Modular Design Refactoring Phase 11
"""

from typing import Dict, List, Any

# Import core components
from .error_detection_core import (
    QuantumError, DetectionResult, QuantumErrorType, 
    DetectionMethod, ErrorSeverity
)

class ErrorDetectionStatistics:
    """
    Error Detection Statistics Calculator
    
    Provides comprehensive statistics for error detection performance
    """
    
    def __init__(self):
        self.detection_history: List[DetectionResult] = []
        self.error_history: List[QuantumError] = []
        self.method_performance: Dict[DetectionMethod, Dict[str, Any]] = {}
    
    def add_detection_result(self, result: DetectionResult):
        """Add detection result to statistics"""
        self.detection_history.append(result)
        
        # Add error to history if detected
        if result.error_detected and result.detected_error:
            self.error_history.append(result.detected_error)
        
        # Update method-specific performance
        method = result.detection_method
        if method not in self.method_performance:
            self.method_performance[method] = {
                'total_detections': 0,
                'successful_detections': 0,
                'total_detection_time': 0.0,
                'total_confidence': 0.0,
                'false_positives': 0
            }
        
        stats = self.method_performance[method]
        stats['total_detections'] += 1
        
        if result.error_detected:
            stats['successful_detections'] += 1
        
        stats['total_detection_time'] += result.detection_time
        stats['total_confidence'] += result.detection_confidence
        
        if result.false_positive_probability > 0.5:
            stats['false_positives'] += 1
        
        # Limit history size
        if len(self.detection_history) > 1000:
            self.detection_history = self.detection_history[-500:]
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-500:]
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error detection statistics"""
        if not self.detection_history:
            return self._empty_statistics()
        
        # Overall statistics
        overall_stats = self._calculate_overall_statistics()
        method_specific_stats = self._calculate_method_specific_statistics()
        error_type_stats = self._calculate_error_type_statistics()
        severity_stats = self._calculate_severity_statistics()
        performance_trends = self._calculate_performance_trends()
        
        return {
            'total_detections': len(self.detection_history),
            'total_errors_found': len(self.error_history),
            'overall_statistics': overall_stats,
            'method_specific_statistics': method_specific_stats,
            'error_type_statistics': error_type_stats,
            'severity_statistics': severity_stats,
            'performance_trends': performance_trends
        }
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """Return empty statistics when no detections available"""
        return {
            'total_detections': 0,
            'total_errors_found': 0,
            'overall_statistics': {},
            'method_specific_statistics': {},
            'error_type_statistics': {},
            'severity_statistics': {},
            'performance_trends': {}
        }
    
    def _calculate_overall_statistics(self) -> Dict[str, Any]:
        """Calculate overall detection statistics"""
        if not self.detection_history:
            return {}
        
        total_time = sum(r.detection_time for r in self.detection_history)
        total_confidence = sum(r.detection_confidence for r in self.detection_history)
        errors_detected = sum(1 for r in self.detection_history if r.error_detected)
        
        return {
            'detection_rate': errors_detected / len(self.detection_history),
            'average_detection_time': total_time / len(self.detection_history),
            'average_confidence': total_confidence / len(self.detection_history),
            'total_errors_detected': errors_detected,
            'false_positive_rate': sum(1 for r in self.detection_history if r.false_positive_probability > 0.5) / len(self.detection_history)
        }
    
    def _calculate_method_specific_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by detection method"""
        method_stats = {}
        
        for method, stats in self.method_performance.items():
            if stats['total_detections'] > 0:
                method_stats[method.value] = {
                    'total_detections': stats['total_detections'],
                    'detection_rate': stats['successful_detections'] / stats['total_detections'],
                    'average_detection_time': stats['total_detection_time'] / stats['total_detections'],
                    'average_confidence': stats['total_confidence'] / stats['total_detections'],
                    'false_positive_rate': stats['false_positives'] / stats['total_detections']
                }
        
        return method_stats
    
    def _calculate_error_type_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by error type"""
        if not self.error_history:
            return {}
        
        type_counts = {}
        type_severities = {}
        type_corrections = {}
        
        for error in self.error_history:
            error_type = error.error_type.value
            
            # Count occurrences
            type_counts[error_type] = type_counts.get(error_type, 0) + 1
            
            # Track severities
            if error_type not in type_severities:
                type_severities[error_type] = []
            type_severities[error_type].append(error.get_severity_score())
            
            # Track correction complexity
            if error_type not in type_corrections:
                type_corrections[error_type] = []
            type_corrections[error_type].append(error.correction_complexity)
        
        # Calculate statistics for each type
        type_stats = {}
        for error_type in type_counts:
            type_stats[error_type] = {
                'count': type_counts[error_type],
                'frequency': type_counts[error_type] / len(self.error_history),
                'average_severity': sum(type_severities[error_type]) / len(type_severities[error_type]),
                'average_correction_complexity': sum(type_corrections[error_type]) / len(type_corrections[error_type])
            }
        
        return type_stats
    
    def _calculate_severity_statistics(self) -> Dict[str, Any]:
        """Calculate statistics by error severity"""
        if not self.error_history:
            return {}
        
        severity_counts = {}
        for error in self.error_history:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'severity_distribution': severity_counts,
            'critical_error_rate': severity_counts.get('critical', 0) / len(self.error_history),
            'correctable_error_rate': sum(1 for e in self.error_history if e.is_correctable()) / len(self.error_history)
        }
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(self.detection_history) < 10:
            return {'trend': 'insufficient_data'}
        
        # Split into first and second half
        mid_point = len(self.detection_history) // 2
        first_half = self.detection_history[:mid_point]
        second_half = self.detection_history[mid_point:]
        
        # Calculate metrics for each half
        first_detection_rate = sum(1 for r in first_half if r.error_detected) / len(first_half)
        second_detection_rate = sum(1 for r in second_half if r.error_detected) / len(second_half)
        
        first_avg_time = sum(r.detection_time for r in first_half) / len(first_half)
        second_avg_time = sum(r.detection_time for r in second_half) / len(second_half)
        
        detection_trend = 'improving' if second_detection_rate > first_detection_rate else 'declining'
        speed_trend = 'improving' if second_avg_time < first_avg_time else 'declining'
        
        return {
            'detection_rate_trend': detection_trend,
            'detection_rate_change': second_detection_rate - first_detection_rate,
            'speed_trend': speed_trend,
            'speed_change': second_avg_time - first_avg_time,
            'first_half_detection_rate': first_detection_rate,
            'second_half_detection_rate': second_detection_rate
        }

# Utility functions
def get_error_detection_statistics(detection_system) -> Dict[str, Any]:
    """Get comprehensive error detection statistics"""
    if not hasattr(detection_system, 'detection_results'):
        return {'error': 'no_detection_results'}
    
    results = detection_system.detection_results if hasattr(detection_system, 'detection_results') else []
    if not results:
        return {
            'total_detections': 0,
            'detection_rate': 0.0,
            'average_detection_time': 0.0
        }
    
    total_detections = len(results)
    errors_detected = sum(1 for r in results if getattr(r, 'error_detected', False))
    total_time = sum(getattr(r, 'detection_time', 0.0) for r in results)
    
    return {
        'total_detections': total_detections,
        'errors_detected': errors_detected,
        'detection_rate': errors_detected / total_detections,
        'average_detection_time': total_time / total_detections,
        'available_methods': getattr(detection_system, 'available_methods', []),
        'alt_las_integration': getattr(detection_system, 'alt_las_integration_active', False)
    }

def create_error_detection_statistics() -> ErrorDetectionStatistics:
    """Create error detection statistics calculator"""
    return ErrorDetectionStatistics()

def analyze_detection_batch(results: List[DetectionResult]) -> Dict[str, Any]:
    """Analyze a batch of detection results"""
    if not results:
        return {'error': 'no_results'}
    
    stats = ErrorDetectionStatistics()
    for result in results:
        stats.add_detection_result(result)
    
    return stats.get_comprehensive_statistics()

def get_detection_summary(result: DetectionResult) -> str:
    """Get human-readable detection summary"""
    efficiency = result.get_detection_efficiency()
    grade = result.get_detection_grade()
    
    return (f"{result.detection_method.value} detection "
            f"(Error: {result.error_detected}, "
            f"Efficiency: {efficiency:.1%}/{grade}, "
            f"Confidence: {result.detection_confidence:.1%}, "
            f"Time: {result.detection_time*1000:.1f}ms)")

def get_error_summary(error: QuantumError) -> str:
    """Get human-readable error summary"""
    severity_score = error.get_severity_score()
    quality = error.get_detection_quality()
    
    return (f"{error.error_type.value} error "
            f"(Qubit: {error.qubit_index}, "
            f"Severity: {error.severity.value}/{severity_score:.3f}, "
            f"Quality: {quality}, "
            f"Correctable: {error.is_correctable()}, "
            f"Priority: {error.get_correction_priority()})")

# Export statistics components
__all__ = [
    'ErrorDetectionStatistics',
    'get_error_detection_statistics',
    'create_error_detection_statistics',
    'analyze_detection_batch',
    'get_detection_summary',
    'get_error_summary'
]
