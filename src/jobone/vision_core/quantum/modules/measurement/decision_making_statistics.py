"""
🧠 Decision Making Statistics - Q05.4.1 Statistics Component

Statistics and analysis for Decision Making systems
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q05.4.1 Quantum Decision Making
Priority: CRITICAL - Modular Design Refactoring Phase 13
"""

from typing import Dict, List, Any

# Import core components
from .decision_making_core import DecisionResult, DecisionParameters, DecisionType, DecisionMethod

class DecisionMakingStatistics:
    """
    Decision Making Statistics Calculator
    
    Provides comprehensive statistics for decision making performance
    """
    
    def __init__(self):
        self.decision_history: List[DecisionResult] = []
        self.parameter_history: List[DecisionParameters] = []
        self.method_performance: Dict[DecisionMethod, Dict[str, Any]] = {}
    
    def add_decision_result(self, result: DecisionResult, parameters: DecisionParameters = None):
        """Add decision result to statistics"""
        self.decision_history.append(result)
        
        if parameters:
            self.parameter_history.append(parameters)
        
        # Update method-specific performance
        decision_method = getattr(parameters, 'decision_method', DecisionMethod.QUANTUM_SUPERPOSITION)
        if decision_method not in self.method_performance:
            self.method_performance[decision_method] = {
                'total_decisions': 0,
                'successful_decisions': 0,
                'total_decision_time': 0.0,
                'total_confidence': 0.0,
                'total_quality': 0.0
            }
        
        stats = self.method_performance[decision_method]
        stats['total_decisions'] += 1
        
        if result.chosen_option:
            stats['successful_decisions'] += 1
        
        stats['total_decision_time'] += result.decision_time
        stats['total_confidence'] += result.decision_confidence
        stats['total_quality'] += result.analysis_quality
        
        # Limit history size
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-500:]
        if len(self.parameter_history) > 1000:
            self.parameter_history = self.parameter_history[-500:]
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive decision making statistics"""
        if not self.decision_history:
            return self._empty_statistics()
        
        # Overall statistics
        overall_stats = self._calculate_overall_statistics()
        method_specific_stats = self._calculate_method_specific_statistics()
        type_specific_stats = self._calculate_type_specific_statistics()
        performance_trends = self._calculate_performance_trends()
        quality_analysis = self._calculate_quality_analysis()
        
        return {
            'total_decisions': len(self.decision_history),
            'overall_statistics': overall_stats,
            'method_specific_statistics': method_specific_stats,
            'type_specific_statistics': type_specific_stats,
            'performance_trends': performance_trends,
            'quality_analysis': quality_analysis
        }
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """Return empty statistics when no decisions available"""
        return {
            'total_decisions': 0,
            'overall_statistics': {},
            'method_specific_statistics': {},
            'type_specific_statistics': {},
            'performance_trends': {},
            'quality_analysis': {}
        }
    
    def _calculate_overall_statistics(self) -> Dict[str, Any]:
        """Calculate overall decision statistics"""
        if not self.decision_history:
            return {}
        
        total_time = sum(r.decision_time for r in self.decision_history)
        total_confidence = sum(r.decision_confidence for r in self.decision_history)
        total_quality = sum(r.analysis_quality for r in self.decision_history)
        successful_decisions = sum(1 for r in self.decision_history if r.chosen_option)
        consciousness_enhanced = sum(1 for r in self.decision_history if r.consciousness_contribution > 0)
        
        return {
            'success_rate': successful_decisions / len(self.decision_history),
            'average_decision_time': total_time / len(self.decision_history),
            'average_confidence': total_confidence / len(self.decision_history),
            'average_quality': total_quality / len(self.decision_history),
            'total_successful_decisions': successful_decisions,
            'consciousness_enhanced_decisions': consciousness_enhanced,
            'consciousness_enhancement_rate': consciousness_enhanced / len(self.decision_history)
        }
    
    def _calculate_method_specific_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by decision method"""
        method_stats = {}
        
        for method, stats in self.method_performance.items():
            if stats['total_decisions'] > 0:
                method_stats[method.value] = {
                    'total_decisions': stats['total_decisions'],
                    'success_rate': stats['successful_decisions'] / stats['total_decisions'],
                    'average_decision_time': stats['total_decision_time'] / stats['total_decisions'],
                    'average_confidence': stats['total_confidence'] / stats['total_decisions'],
                    'average_quality': stats['total_quality'] / stats['total_decisions']
                }
        
        return method_stats
    
    def _calculate_type_specific_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by decision type"""
        type_counts = {}
        type_confidence = {}
        type_quality = {}
        
        for result in self.decision_history:
            decision_type = result.decision_type.value
            
            # Count occurrences
            type_counts[decision_type] = type_counts.get(decision_type, 0) + 1
            
            # Track confidence
            if decision_type not in type_confidence:
                type_confidence[decision_type] = []
            type_confidence[decision_type].append(result.decision_confidence)
            
            # Track quality
            if decision_type not in type_quality:
                type_quality[decision_type] = []
            type_quality[decision_type].append(result.analysis_quality)
        
        # Calculate statistics for each type
        type_stats = {}
        for decision_type in type_counts:
            type_stats[decision_type] = {
                'count': type_counts[decision_type],
                'frequency': type_counts[decision_type] / len(self.decision_history),
                'average_confidence': sum(type_confidence[decision_type]) / len(type_confidence[decision_type]),
                'average_quality': sum(type_quality[decision_type]) / len(type_quality[decision_type])
            }
        
        return type_stats
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(self.decision_history) < 10:
            return {'trend': 'insufficient_data'}
        
        # Split into first and second half
        mid_point = len(self.decision_history) // 2
        first_half = self.decision_history[:mid_point]
        second_half = self.decision_history[mid_point:]
        
        # Calculate metrics for each half
        first_success_rate = sum(1 for r in first_half if r.chosen_option) / len(first_half)
        second_success_rate = sum(1 for r in second_half if r.chosen_option) / len(second_half)
        
        first_avg_confidence = sum(r.decision_confidence for r in first_half) / len(first_half)
        second_avg_confidence = sum(r.decision_confidence for r in second_half) / len(second_half)
        
        first_avg_quality = sum(r.analysis_quality for r in first_half) / len(first_half)
        second_avg_quality = sum(r.analysis_quality for r in second_half) / len(second_half)
        
        success_trend = 'improving' if second_success_rate > first_success_rate else 'declining'
        confidence_trend = 'improving' if second_avg_confidence > first_avg_confidence else 'declining'
        quality_trend = 'improving' if second_avg_quality > first_avg_quality else 'declining'
        
        return {
            'success_rate_trend': success_trend,
            'success_rate_change': second_success_rate - first_success_rate,
            'confidence_trend': confidence_trend,
            'confidence_change': second_avg_confidence - first_avg_confidence,
            'quality_trend': quality_trend,
            'quality_change': second_avg_quality - first_avg_quality,
            'first_half_success_rate': first_success_rate,
            'second_half_success_rate': second_success_rate
        }
    
    def _calculate_quality_analysis(self) -> Dict[str, Any]:
        """Calculate quality analysis"""
        if not self.decision_history:
            return {}
        
        # Quality distribution
        quality_grades = {}
        confidence_levels = {}
        
        for result in self.decision_history:
            grade = result.get_decision_grade()
            quality_grades[grade] = quality_grades.get(grade, 0) + 1
            
            confidence_level = result.get_confidence_level()
            confidence_levels[confidence_level] = confidence_levels.get(confidence_level, 0) + 1
        
        # Calculate quality metrics
        high_quality_decisions = sum(1 for r in self.decision_history if r.analysis_quality >= 0.8)
        high_confidence_decisions = sum(1 for r in self.decision_history if r.decision_confidence >= 0.8)
        
        return {
            'quality_distribution': quality_grades,
            'confidence_distribution': confidence_levels,
            'high_quality_rate': high_quality_decisions / len(self.decision_history),
            'high_confidence_rate': high_confidence_decisions / len(self.decision_history),
            'consciousness_contribution_rate': sum(1 for r in self.decision_history if r.consciousness_contribution > 0) / len(self.decision_history)
        }

# Utility functions
def get_decision_making_statistics(decision_system) -> Dict[str, Any]:
    """Get comprehensive decision making statistics"""
    if not hasattr(decision_system, 'decision_results'):
        return {'error': 'no_decision_results'}
    
    results = decision_system.decision_results if hasattr(decision_system, 'decision_results') else []
    if not results:
        return {
            'total_decisions': 0,
            'success_rate': 0.0,
            'average_confidence': 0.0
        }
    
    total_decisions = len(results)
    successful_decisions = sum(1 for r in results if getattr(r, 'chosen_option', None))
    total_confidence = sum(getattr(r, 'decision_confidence', 0.0) for r in results)
    
    return {
        'total_decisions': total_decisions,
        'successful_decisions': successful_decisions,
        'success_rate': successful_decisions / total_decisions,
        'average_confidence': total_confidence / total_decisions,
        'available_decision_methods': getattr(decision_system, 'available_decision_methods', []),
        'consciousness_integration': getattr(decision_system, 'consciousness_integration_active', False)
    }

def create_decision_making_statistics() -> DecisionMakingStatistics:
    """Create decision making statistics calculator"""
    return DecisionMakingStatistics()

def analyze_decision_batch(results: List[DecisionResult], parameters: List[DecisionParameters] = None) -> Dict[str, Any]:
    """Analyze a batch of decision results"""
    if not results:
        return {'error': 'no_results'}
    
    stats = DecisionMakingStatistics()
    for i, result in enumerate(results):
        param = parameters[i] if parameters and i < len(parameters) else None
        stats.add_decision_result(result, param)
    
    return stats.get_comprehensive_statistics()

def get_decision_summary(result: DecisionResult) -> str:
    """Get human-readable decision summary"""
    quality = result.analysis_quality
    grade = result.get_decision_grade()
    confidence_level = result.get_confidence_level()
    
    return (f"{result.decision_type.value} decision "
            f"(Choice: {result.chosen_option}, "
            f"Confidence: {confidence_level}/{result.decision_confidence:.1%}, "
            f"Quality: {grade}/{quality:.3f}, "
            f"Time: {result.decision_time*1000:.1f}ms)")

def get_parameters_summary(parameters: DecisionParameters) -> str:
    """Get human-readable parameters summary"""
    complexity = parameters.get_decision_complexity()
    consciousness_factor = parameters.get_consciousness_factor()
    
    return (f"{parameters.decision_type.value} parameters "
            f"(Method: {parameters.decision_method.value}, "
            f"Options: {len(parameters.available_options)}, "
            f"Complexity: {complexity}/5, "
            f"Consciousness: {consciousness_factor:.1%})")

def compare_decision_methods(results: List[DecisionResult], parameters: List[DecisionParameters] = None) -> Dict[str, Any]:
    """Compare performance across decision methods"""
    if not results:
        return {'error': 'no_results'}

    method_performance = {}

    for i, result in enumerate(results):
        param = parameters[i] if parameters and i < len(parameters) else None
        method = param.decision_method.value if param else 'unknown'

        if method not in method_performance:
            method_performance[method] = {'count': 0, 'success_rate': 0.0, 'avg_confidence': 0.0, 'avg_quality': 0.0}

        stats = method_performance[method]
        stats['count'] += 1
        stats['success_rate'] += 1 if result.chosen_option else 0
        stats['avg_confidence'] += result.decision_confidence
        stats['avg_quality'] += result.analysis_quality

    # Calculate averages
    for stats in method_performance.values():
        if stats['count'] > 0:
            stats['success_rate'] /= stats['count']
            stats['avg_confidence'] /= stats['count']
            stats['avg_quality'] /= stats['count']

    return {
        'method_comparison': method_performance,
        'best_quality_method': max(method_performance.keys(), key=lambda k: method_performance[k]['avg_quality']),
        'best_confidence_method': max(method_performance.keys(), key=lambda k: method_performance[k]['avg_confidence']),
        'most_reliable_method': max(method_performance.keys(), key=lambda k: method_performance[k]['success_rate'])
    }

# Export statistics components
__all__ = [
    'DecisionMakingStatistics',
    'get_decision_making_statistics',
    'create_decision_making_statistics',
    'analyze_decision_batch',
    'get_decision_summary',
    'get_parameters_summary',
    'compare_decision_methods'
]
