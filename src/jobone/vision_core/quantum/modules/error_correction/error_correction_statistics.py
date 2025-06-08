"""
🛡️ Error Correction Statistics - Q05.2.2 Statistics Component

Statistics and analysis for Error Correction systems
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q05.2.2 Quantum Error Correction Codes
Priority: CRITICAL - Modular Design Refactoring Phase 10
"""

from typing import Dict, List, Any

# Import core components
from .error_correction_core import CorrectionResult, CorrectionCode, ErrorCorrectionCode

class ErrorCorrectionStatistics:
    """
    Error Correction Statistics Calculator
    
    Provides comprehensive statistics for error correction performance
    """
    
    def __init__(self):
        self.correction_history: List[CorrectionResult] = []
        self.code_performance: Dict[ErrorCorrectionCode, Dict[str, Any]] = {}
    
    def add_correction_result(self, result: CorrectionResult):
        """Add correction result to statistics"""
        self.correction_history.append(result)
        
        # Update code-specific performance
        code_type = result.correction_code
        if code_type not in self.code_performance:
            self.code_performance[code_type] = {
                'total_corrections': 0,
                'successful_corrections': 0,
                'total_correction_time': 0.0,
                'total_fidelity_improvement': 0.0,
                'total_errors_detected': 0,
                'total_errors_corrected': 0
            }
        
        stats = self.code_performance[code_type]
        stats['total_corrections'] += 1
        
        if result.correction_successful:
            stats['successful_corrections'] += 1
        
        stats['total_correction_time'] += result.correction_time
        stats['total_fidelity_improvement'] += result.fidelity_improvement
        stats['total_errors_detected'] += len(result.detected_errors)
        stats['total_errors_corrected'] += len(result.corrected_errors)
        
        # Limit history size
        if len(self.correction_history) > 1000:
            self.correction_history = self.correction_history[-500:]
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error correction statistics"""
        if not self.correction_history:
            return self._empty_statistics()
        
        # Overall statistics
        total_corrections = len(self.correction_history)
        successful_corrections = sum(1 for r in self.correction_history if r.correction_successful)
        
        # Performance metrics
        overall_stats = self._calculate_overall_statistics()
        code_specific_stats = self._calculate_code_specific_statistics()
        performance_trends = self._calculate_performance_trends()
        
        return {
            'total_corrections': total_corrections,
            'successful_corrections': successful_corrections,
            'success_rate': successful_corrections / total_corrections,
            'overall_statistics': overall_stats,
            'code_specific_statistics': code_specific_stats,
            'performance_trends': performance_trends
        }
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """Return empty statistics when no corrections available"""
        return {
            'total_corrections': 0,
            'success_rate': 0.0,
            'overall_statistics': {},
            'code_specific_statistics': {},
            'performance_trends': {}
        }
    
    def _calculate_overall_statistics(self) -> Dict[str, Any]:
        """Calculate overall correction statistics"""
        if not self.correction_history:
            return {}
        
        total_time = sum(r.correction_time for r in self.correction_history)
        total_fidelity_improvement = sum(r.fidelity_improvement for r in self.correction_history)
        total_detected = sum(len(r.detected_errors) for r in self.correction_history)
        total_corrected = sum(len(r.corrected_errors) for r in self.correction_history)
        
        return {
            'average_correction_time': total_time / len(self.correction_history),
            'average_fidelity_improvement': total_fidelity_improvement / len(self.correction_history),
            'total_errors_detected': total_detected,
            'total_errors_corrected': total_corrected,
            'error_correction_efficiency': total_corrected / max(1, total_detected),
            'consciousness_assisted_corrections': sum(1 for r in self.correction_history if r.consciousness_assistance > 0)
        }
    
    def _calculate_code_specific_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by error correction code"""
        code_stats = {}
        
        for code_type, stats in self.code_performance.items():
            if stats['total_corrections'] > 0:
                code_stats[code_type.value] = {
                    'total_corrections': stats['total_corrections'],
                    'success_rate': stats['successful_corrections'] / stats['total_corrections'],
                    'average_correction_time': stats['total_correction_time'] / stats['total_corrections'],
                    'average_fidelity_improvement': stats['total_fidelity_improvement'] / stats['total_corrections'],
                    'error_correction_efficiency': stats['total_errors_corrected'] / max(1, stats['total_errors_detected'])
                }
        
        return code_stats
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(self.correction_history) < 10:
            return {'trend': 'insufficient_data'}
        
        # Split into first and second half
        mid_point = len(self.correction_history) // 2
        first_half = self.correction_history[:mid_point]
        second_half = self.correction_history[mid_point:]
        
        # Calculate metrics for each half
        first_success_rate = sum(1 for r in first_half if r.correction_successful) / len(first_half)
        second_success_rate = sum(1 for r in second_half if r.correction_successful) / len(second_half)
        
        first_avg_time = sum(r.correction_time for r in first_half) / len(first_half)
        second_avg_time = sum(r.correction_time for r in second_half) / len(second_half)
        
        success_trend = 'improving' if second_success_rate > first_success_rate else 'declining'
        speed_trend = 'improving' if second_avg_time < first_avg_time else 'declining'
        
        return {
            'success_rate_trend': success_trend,
            'success_rate_change': second_success_rate - first_success_rate,
            'speed_trend': speed_trend,
            'speed_change': second_avg_time - first_avg_time,
            'first_half_success_rate': first_success_rate,
            'second_half_success_rate': second_success_rate
        }

# Utility functions
def get_error_correction_statistics(correction_system) -> Dict[str, Any]:
    """Get comprehensive error correction statistics"""
    if not hasattr(correction_system, 'correction_results'):
        return {'error': 'no_correction_results'}
    
    results = correction_system.correction_results
    if not results:
        return {
            'total_corrections': 0,
            'success_rate': 0.0,
            'average_correction_time': 0.0
        }
    
    total_corrections = len(results)
    successful_corrections = sum(1 for r in results if r.correction_successful)
    total_time = sum(r.correction_time for r in results)
    
    return {
        'total_corrections': total_corrections,
        'successful_corrections': successful_corrections,
        'success_rate': successful_corrections / total_corrections,
        'average_correction_time': total_time / total_corrections,
        'available_codes': getattr(correction_system, 'available_codes', {}),
        'alt_las_integration': getattr(correction_system, 'alt_las_integration_active', False)
    }

def create_error_correction_statistics() -> ErrorCorrectionStatistics:
    """Create error correction statistics calculator"""
    return ErrorCorrectionStatistics()

def analyze_correction_batch(results: List[CorrectionResult]) -> Dict[str, Any]:
    """Analyze a batch of correction results"""
    if not results:
        return {'error': 'no_results'}
    
    stats = ErrorCorrectionStatistics()
    for result in results:
        stats.add_correction_result(result)
    
    return stats.get_comprehensive_statistics()

def get_correction_summary(result: CorrectionResult) -> str:
    """Get human-readable correction summary"""
    efficiency = result.get_correction_efficiency()
    grade = result.get_correction_grade()
    
    return (f"{result.correction_code.value} correction "
            f"(Success: {result.correction_successful}, "
            f"Efficiency: {efficiency:.1%}/{grade}, "
            f"Errors: {len(result.detected_errors)}→{len(result.corrected_errors)}, "
            f"Fidelity: {result.fidelity_improvement:+.3f}, "
            f"Time: {result.correction_time*1000:.1f}ms)")

def get_code_summary(code: CorrectionCode) -> str:
    """Get human-readable code summary"""
    efficiency = code.get_efficiency_score()
    grade = code.get_code_grade()
    
    return (f"{code.code_type.value} "
            f"({code.n_physical_qubits}→{code.n_logical_qubits} qubits, "
            f"Distance: {code.code_distance}, "
            f"Success rate: {code.correction_success_rate:.1%}, "
            f"Efficiency: {efficiency:.3f}/{grade})")

def compare_codes(codes: List[CorrectionCode]) -> Dict[str, Any]:
    """Compare multiple correction codes"""
    if not codes:
        return {'error': 'no_codes'}
    
    comparison = {
        'total_codes': len(codes),
        'best_efficiency': max(code.get_efficiency_score() for code in codes),
        'best_success_rate': max(code.correction_success_rate for code in codes),
        'most_efficient_code': max(codes, key=lambda c: c.get_efficiency_score()).code_type.value,
        'highest_success_code': max(codes, key=lambda c: c.correction_success_rate).code_type.value,
        'code_details': [code.get_summary() for code in codes]
    }
    
    return comparison

# Export statistics components
__all__ = [
    'ErrorCorrectionStatistics',
    'get_error_correction_statistics',
    'create_error_correction_statistics',
    'analyze_correction_batch',
    'get_correction_summary',
    'get_code_summary',
    'compare_codes'
]
