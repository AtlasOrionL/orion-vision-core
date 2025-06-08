"""
👁️ Measurement Statistics - Q4.1 Statistics Component

Statistics and utilities for Non-Demolitional Measurement Units (NDMU)
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q4.1 Non-Demolitional Measurement Units
Priority: CRITICAL - Modular Design Refactoring Phase 6
"""

from typing import Dict, List, Any

# Import core components
from .measurement_core import MeasurementResult, MeasurementMode, MeasurementType

class MeasurementStatistics:
    """
    Measurement Statistics Calculator
    
    Provides comprehensive statistics for NDMU measurements.
    """
    
    def __init__(self):
        self.measurement_history: List[MeasurementResult] = []
    
    def add_measurement(self, result: MeasurementResult):
        """Add measurement result to statistics"""
        self.measurement_history.append(result)
        
        # Limit history size
        if len(self.measurement_history) > 1000:
            self.measurement_history = self.measurement_history[-500:]
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive NDMU statistics"""
        if not self.measurement_history:
            return self._empty_statistics()
        
        # Basic counts
        total_measurements = len(self.measurement_history)
        successful_ndm = sum(1 for r in self.measurement_history if r.is_non_demolitional())
        state_preserved = sum(1 for r in self.measurement_history if r.original_state_preserved)
        
        # Quality metrics
        total_quality = sum(r.calculate_measurement_quality() for r in self.measurement_history)
        average_quality = total_quality / total_measurements
        
        # Disturbance metrics
        total_disturbance = sum(r.state_disturbance for r in self.measurement_history)
        average_disturbance = total_disturbance / total_measurements
        
        # Coherence loss metrics
        total_coherence_loss = sum(r.coherence_loss for r in self.measurement_history)
        average_coherence_loss = total_coherence_loss / total_measurements
        
        # Recent performance (last 100 measurements)
        recent_measurements = self.measurement_history[-100:]
        recent_ndm = sum(1 for r in recent_measurements if r.is_non_demolitional())
        recent_ndm_rate = recent_ndm / len(recent_measurements) if recent_measurements else 0.0
        
        # Mode-specific statistics
        mode_stats = self._calculate_mode_statistics()
        
        # Quality distribution
        quality_distribution = self._calculate_quality_distribution()
        
        # Performance trends
        performance_trends = self._calculate_performance_trends()
        
        return {
            'total_measurements': total_measurements,
            'successful_ndm_count': successful_ndm,
            'ndm_success_rate': successful_ndm / total_measurements,
            'state_preservation_rate': state_preserved / total_measurements,
            'recent_ndm_rate': recent_ndm_rate,
            'average_quality': average_quality,
            'average_disturbance': average_disturbance,
            'average_coherence_loss': average_coherence_loss,
            'mode_statistics': mode_stats,
            'quality_distribution': quality_distribution,
            'performance_trends': performance_trends
        }
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """Return empty statistics when no measurements available"""
        return {
            'total_measurements': 0,
            'ndm_success_rate': 0.0,
            'state_preservation_rate': 0.0,
            'average_quality': 0.0,
            'average_disturbance': 0.0,
            'average_coherence_loss': 0.0,
            'mode_statistics': {},
            'quality_distribution': {},
            'performance_trends': {}
        }
    
    def _calculate_mode_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by measurement mode"""
        mode_stats = {}
        
        for mode in MeasurementMode:
            mode_measurements = [r for r in self.measurement_history if r.measurement_mode == mode]
            
            if mode_measurements:
                total_quality = sum(r.calculate_measurement_quality() for r in mode_measurements)
                ndm_count = sum(1 for r in mode_measurements if r.is_non_demolitional())
                
                mode_stats[mode.value] = {
                    'count': len(mode_measurements),
                    'ndm_success_rate': ndm_count / len(mode_measurements),
                    'average_quality': total_quality / len(mode_measurements),
                    'average_disturbance': sum(r.state_disturbance for r in mode_measurements) / len(mode_measurements)
                }
        
        return mode_stats
    
    def _calculate_quality_distribution(self) -> Dict[str, int]:
        """Calculate quality grade distribution"""
        distribution = {'A+': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for result in self.measurement_history:
            grade = result.get_quality_grade()
            distribution[grade] += 1
        
        return distribution
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(self.measurement_history) < 10:
            return {'trend': 'insufficient_data'}
        
        # Split into first and second half
        mid_point = len(self.measurement_history) // 2
        first_half = self.measurement_history[:mid_point]
        second_half = self.measurement_history[mid_point:]
        
        # Calculate metrics for each half
        first_quality = sum(r.calculate_measurement_quality() for r in first_half) / len(first_half)
        second_quality = sum(r.calculate_measurement_quality() for r in second_half) / len(second_half)
        
        first_ndm_rate = sum(1 for r in first_half if r.is_non_demolitional()) / len(first_half)
        second_ndm_rate = sum(1 for r in second_half if r.is_non_demolitional()) / len(second_half)
        
        quality_trend = 'improving' if second_quality > first_quality else 'declining'
        ndm_trend = 'improving' if second_ndm_rate > first_ndm_rate else 'declining'
        
        return {
            'quality_trend': quality_trend,
            'quality_change': second_quality - first_quality,
            'ndm_trend': ndm_trend,
            'ndm_rate_change': second_ndm_rate - first_ndm_rate,
            'first_half_quality': first_quality,
            'second_half_quality': second_quality
        }

# Utility functions
def create_measurement_statistics() -> MeasurementStatistics:
    """Create measurement statistics calculator"""
    return MeasurementStatistics()

def analyze_measurement_batch(results: List[MeasurementResult]) -> Dict[str, Any]:
    """Analyze a batch of measurement results"""
    if not results:
        return {'error': 'no_measurements'}
    
    stats = MeasurementStatistics()
    for result in results:
        stats.add_measurement(result)
    
    return stats.get_comprehensive_statistics()

def get_measurement_summary(result: MeasurementResult) -> str:
    """Get human-readable measurement summary"""
    quality = result.calculate_measurement_quality()
    grade = result.get_quality_grade()
    ndm_status = "NDM" if result.is_non_demolitional() else "Classical"
    
    return (f"{ndm_status} measurement of {result.target_type} "
            f"(Quality: {quality:.3f}/{grade}, "
            f"Disturbance: {result.state_disturbance:.3f}, "
            f"Duration: {result.measurement_duration*1000:.1f}ms)")

# Export statistics components
__all__ = [
    'MeasurementStatistics',
    'create_measurement_statistics',
    'analyze_measurement_batch',
    'get_measurement_summary'
]
