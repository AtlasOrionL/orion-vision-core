"""
⚛️ Field Interactions Statistics - Q05.3.1 Statistics Component

Statistics and analysis for Field Interaction systems
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q05.3.1 Field Interaction Modeling
Priority: CRITICAL - Modular Design Refactoring Phase 12
"""

from typing import Dict, List, Any

# Import core components
from .field_interactions_core import InteractionResult, InteractionParameters, InteractionType, CouplingMechanism

class FieldInteractionStatistics:
    """
    Field Interaction Statistics Calculator
    
    Provides comprehensive statistics for field interaction performance
    """
    
    def __init__(self):
        self.interaction_history: List[InteractionResult] = []
        self.parameter_history: List[InteractionParameters] = []
        self.type_performance: Dict[InteractionType, Dict[str, Any]] = {}
    
    def add_interaction_result(self, result: InteractionResult, parameters: InteractionParameters = None):
        """Add interaction result to statistics"""
        self.interaction_history.append(result)
        
        if parameters:
            self.parameter_history.append(parameters)
        
        # Update type-specific performance
        interaction_type = result.interaction_type
        if interaction_type not in self.type_performance:
            self.type_performance[interaction_type] = {
                'total_interactions': 0,
                'successful_interactions': 0,
                'total_computation_time': 0.0,
                'total_coupling_efficiency': 0.0,
                'total_energy_transfer': 0.0,
                'total_entanglement_generation': 0.0
            }
        
        stats = self.type_performance[interaction_type]
        stats['total_interactions'] += 1
        
        if result.interaction_successful:
            stats['successful_interactions'] += 1
        
        stats['total_computation_time'] += result.computation_time
        stats['total_coupling_efficiency'] += result.coupling_efficiency
        stats['total_energy_transfer'] += result.energy_transfer
        stats['total_entanglement_generation'] += result.entanglement_generation
        
        # Limit history size
        if len(self.interaction_history) > 1000:
            self.interaction_history = self.interaction_history[-500:]
        if len(self.parameter_history) > 1000:
            self.parameter_history = self.parameter_history[-500:]
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive field interaction statistics"""
        if not self.interaction_history:
            return self._empty_statistics()
        
        # Overall statistics
        overall_stats = self._calculate_overall_statistics()
        type_specific_stats = self._calculate_type_specific_statistics()
        performance_trends = self._calculate_performance_trends()
        quality_analysis = self._calculate_quality_analysis()
        
        return {
            'total_interactions': len(self.interaction_history),
            'overall_statistics': overall_stats,
            'type_specific_statistics': type_specific_stats,
            'performance_trends': performance_trends,
            'quality_analysis': quality_analysis
        }
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """Return empty statistics when no interactions available"""
        return {
            'total_interactions': 0,
            'overall_statistics': {},
            'type_specific_statistics': {},
            'performance_trends': {},
            'quality_analysis': {}
        }
    
    def _calculate_overall_statistics(self) -> Dict[str, Any]:
        """Calculate overall interaction statistics"""
        if not self.interaction_history:
            return {}
        
        total_time = sum(r.computation_time for r in self.interaction_history)
        total_coupling_efficiency = sum(r.coupling_efficiency for r in self.interaction_history)
        total_energy_transfer = sum(r.energy_transfer for r in self.interaction_history)
        total_entanglement = sum(r.entanglement_generation for r in self.interaction_history)
        successful_interactions = sum(1 for r in self.interaction_history if r.interaction_successful)
        
        return {
            'success_rate': successful_interactions / len(self.interaction_history),
            'average_computation_time': total_time / len(self.interaction_history),
            'average_coupling_efficiency': total_coupling_efficiency / len(self.interaction_history),
            'average_energy_transfer': total_energy_transfer / len(self.interaction_history),
            'average_entanglement_generation': total_entanglement / len(self.interaction_history),
            'total_successful_interactions': successful_interactions,
            'consciousness_enhanced_interactions': sum(1 for r in self.interaction_history if r.consciousness_enhancement > 0)
        }
    
    def _calculate_type_specific_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by interaction type"""
        type_stats = {}
        
        for interaction_type, stats in self.type_performance.items():
            if stats['total_interactions'] > 0:
                type_stats[interaction_type.value] = {
                    'total_interactions': stats['total_interactions'],
                    'success_rate': stats['successful_interactions'] / stats['total_interactions'],
                    'average_computation_time': stats['total_computation_time'] / stats['total_interactions'],
                    'average_coupling_efficiency': stats['total_coupling_efficiency'] / stats['total_interactions'],
                    'average_energy_transfer': stats['total_energy_transfer'] / stats['total_interactions'],
                    'average_entanglement_generation': stats['total_entanglement_generation'] / stats['total_interactions']
                }
        
        return type_stats
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(self.interaction_history) < 10:
            return {'trend': 'insufficient_data'}
        
        # Split into first and second half
        mid_point = len(self.interaction_history) // 2
        first_half = self.interaction_history[:mid_point]
        second_half = self.interaction_history[mid_point:]
        
        # Calculate metrics for each half
        first_success_rate = sum(1 for r in first_half if r.interaction_successful) / len(first_half)
        second_success_rate = sum(1 for r in second_half if r.interaction_successful) / len(second_half)
        
        first_avg_efficiency = sum(r.coupling_efficiency for r in first_half) / len(first_half)
        second_avg_efficiency = sum(r.coupling_efficiency for r in second_half) / len(second_half)
        
        first_avg_time = sum(r.computation_time for r in first_half) / len(first_half)
        second_avg_time = sum(r.computation_time for r in second_half) / len(second_half)
        
        success_trend = 'improving' if second_success_rate > first_success_rate else 'declining'
        efficiency_trend = 'improving' if second_avg_efficiency > first_avg_efficiency else 'declining'
        speed_trend = 'improving' if second_avg_time < first_avg_time else 'declining'
        
        return {
            'success_rate_trend': success_trend,
            'success_rate_change': second_success_rate - first_success_rate,
            'efficiency_trend': efficiency_trend,
            'efficiency_change': second_avg_efficiency - first_avg_efficiency,
            'speed_trend': speed_trend,
            'speed_change': second_avg_time - first_avg_time,
            'first_half_success_rate': first_success_rate,
            'second_half_success_rate': second_success_rate
        }
    
    def _calculate_quality_analysis(self) -> Dict[str, Any]:
        """Calculate quality analysis"""
        if not self.interaction_history:
            return {}
        
        # Quality distribution
        quality_grades = {}
        performance_scores = []
        
        for result in self.interaction_history:
            grade = result.get_interaction_grade()
            quality_grades[grade] = quality_grades.get(grade, 0) + 1
            performance_scores.append(result.get_performance_score())
        
        # Calculate quality metrics
        avg_performance = sum(performance_scores) / len(performance_scores)
        high_quality_interactions = sum(1 for r in self.interaction_history if r.get_interaction_quality() >= 0.8)
        
        return {
            'quality_distribution': quality_grades,
            'average_performance_score': avg_performance,
            'high_quality_rate': high_quality_interactions / len(self.interaction_history),
            'consciousness_enhancement_rate': sum(1 for r in self.interaction_history if r.consciousness_enhancement > 0) / len(self.interaction_history)
        }

# Utility functions
def get_field_interaction_statistics(interaction_system) -> Dict[str, Any]:
    """Get comprehensive field interaction statistics"""
    if not hasattr(interaction_system, 'interaction_results'):
        return {'error': 'no_interaction_results'}
    
    results = interaction_system.interaction_results if hasattr(interaction_system, 'interaction_results') else []
    if not results:
        return {
            'total_interactions': 0,
            'success_rate': 0.0,
            'average_coupling_efficiency': 0.0
        }
    
    total_interactions = len(results)
    successful_interactions = sum(1 for r in results if getattr(r, 'interaction_successful', False))
    total_efficiency = sum(getattr(r, 'coupling_efficiency', 0.0) for r in results)
    
    return {
        'total_interactions': total_interactions,
        'successful_interactions': successful_interactions,
        'success_rate': successful_interactions / total_interactions,
        'average_coupling_efficiency': total_efficiency / total_interactions,
        'available_interaction_types': getattr(interaction_system, 'available_interaction_types', []),
        'alt_las_integration': getattr(interaction_system, 'alt_las_integration_active', False)
    }

def create_field_interaction_statistics() -> FieldInteractionStatistics:
    """Create field interaction statistics calculator"""
    return FieldInteractionStatistics()

def analyze_interaction_batch(results: List[InteractionResult], parameters: List[InteractionParameters] = None) -> Dict[str, Any]:
    """Analyze a batch of interaction results"""
    if not results:
        return {'error': 'no_results'}
    
    stats = FieldInteractionStatistics()
    for i, result in enumerate(results):
        param = parameters[i] if parameters and i < len(parameters) else None
        stats.add_interaction_result(result, param)
    
    return stats.get_comprehensive_statistics()

def get_interaction_summary(result: InteractionResult) -> str:
    """Get human-readable interaction summary"""
    quality = result.get_interaction_quality()
    grade = result.get_interaction_grade()
    
    return (f"{result.interaction_type.value} interaction "
            f"(Success: {result.interaction_successful}, "
            f"Quality: {quality:.3f}/{grade}, "
            f"Efficiency: {result.coupling_efficiency:.1%}, "
            f"Energy transfer: {result.energy_transfer:.3f}, "
            f"Time: {result.computation_time*1000:.1f}ms)")

def get_parameters_summary(parameters: InteractionParameters) -> str:
    """Get human-readable parameters summary"""
    complexity = parameters.get_interaction_complexity()
    efficiency_estimate = parameters.get_coupling_efficiency_estimate()
    
    return (f"{parameters.interaction_type.value} parameters "
            f"(Coupling: {parameters.coupling_strength:.3f}, "
            f"Fields: {parameters.field_count}, "
            f"Steps: {parameters.time_steps}, "
            f"Complexity: {complexity}/5, "
            f"Efficiency estimate: {efficiency_estimate:.1%})")

def compare_interaction_types(results: List[InteractionResult]) -> Dict[str, Any]:
    """Compare performance across interaction types"""
    if not results:
        return {'error': 'no_results'}
    
    type_performance = {}
    
    for result in results:
        interaction_type = result.interaction_type.value
        if interaction_type not in type_performance:
            type_performance[interaction_type] = {
                'count': 0,
                'success_rate': 0.0,
                'avg_quality': 0.0,
                'avg_efficiency': 0.0
            }
        
        stats = type_performance[interaction_type]
        stats['count'] += 1
        stats['success_rate'] += 1 if result.interaction_successful else 0
        stats['avg_quality'] += result.get_interaction_quality()
        stats['avg_efficiency'] += result.coupling_efficiency
    
    # Calculate averages
    for stats in type_performance.values():
        if stats['count'] > 0:
            stats['success_rate'] /= stats['count']
            stats['avg_quality'] /= stats['count']
            stats['avg_efficiency'] /= stats['count']
    
    return {
        'type_comparison': type_performance,
        'best_quality_type': max(type_performance.keys(), key=lambda k: type_performance[k]['avg_quality']),
        'best_efficiency_type': max(type_performance.keys(), key=lambda k: type_performance[k]['avg_efficiency']),
        'most_reliable_type': max(type_performance.keys(), key=lambda k: type_performance[k]['success_rate'])
    }

# Export statistics components
__all__ = [
    'FieldInteractionStatistics',
    'get_field_interaction_statistics',
    'create_field_interaction_statistics',
    'analyze_interaction_batch',
    'get_interaction_summary',
    'get_parameters_summary',
    'compare_interaction_types'
]
