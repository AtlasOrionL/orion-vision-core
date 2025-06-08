"""
🧠 Evolution Statistics - Q4.2 Statistics Component

Statistics and utilities for Measurement Induced Evolution
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q4.2 Measurement Induced Evolution & Quantum Learning Rate
Priority: CRITICAL - Modular Design Refactoring Phase 7
"""

from typing import Dict, List, Any

# Import core components
from .evolution_core import EvolutionEvent, LearningMode, EvolutionType

class EvolutionStatistics:
    """
    Evolution Statistics Calculator
    
    Provides comprehensive statistics for evolution events.
    """
    
    def __init__(self):
        self.evolution_history: List[EvolutionEvent] = []
    
    def add_evolution_event(self, event: EvolutionEvent):
        """Add evolution event to statistics"""
        self.evolution_history.append(event)
        
        # Limit history size
        if len(self.evolution_history) > 1000:
            self.evolution_history = self.evolution_history[-500:]
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive evolution statistics"""
        if not self.evolution_history:
            return self._empty_statistics()
        
        # Basic counts
        total_evolutions = len(self.evolution_history)
        significant_evolutions = sum(1 for e in self.evolution_history if e.is_significant_evolution())
        successful_learnings = sum(1 for e in self.evolution_history if e.learning_strength > 0.5)
        
        # Learning metrics
        total_learning_strength = sum(e.learning_strength for e in self.evolution_history)
        average_learning_strength = total_learning_strength / total_evolutions
        
        # Evolution impact metrics
        total_impact = sum(e.calculate_evolution_impact() for e in self.evolution_history)
        average_impact = total_impact / total_evolutions
        
        # Coherence metrics
        coherence_changes = [e.coherence_change for e in self.evolution_history]
        average_coherence_change = sum(coherence_changes) / total_evolutions
        positive_coherence_changes = sum(1 for c in coherence_changes if c > 0)
        
        # Information metrics
        information_gains = [e.information_gain for e in self.evolution_history]
        average_information_gain = sum(information_gains) / total_evolutions
        total_information_gain = sum(information_gains)
        
        # Recent performance (last 100 events)
        recent_events = self.evolution_history[-100:]
        recent_significant = sum(1 for e in recent_events if e.is_significant_evolution())
        recent_significance_rate = recent_significant / len(recent_events) if recent_events else 0.0
        
        # Learning mode statistics
        mode_stats = self._calculate_mode_statistics()
        
        # Impact distribution
        impact_distribution = self._calculate_impact_distribution()
        
        # Performance trends
        performance_trends = self._calculate_performance_trends()
        
        return {
            'total_evolutions': total_evolutions,
            'significant_evolutions': significant_evolutions,
            'significance_rate': significant_evolutions / total_evolutions,
            'successful_learnings': successful_learnings,
            'learning_success_rate': successful_learnings / total_evolutions,
            'recent_significance_rate': recent_significance_rate,
            'average_learning_strength': average_learning_strength,
            'average_impact': average_impact,
            'average_coherence_change': average_coherence_change,
            'positive_coherence_rate': positive_coherence_changes / total_evolutions,
            'average_information_gain': average_information_gain,
            'total_information_gain': total_information_gain,
            'mode_statistics': mode_stats,
            'impact_distribution': impact_distribution,
            'performance_trends': performance_trends
        }
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """Return empty statistics when no events available"""
        return {
            'total_evolutions': 0,
            'significance_rate': 0.0,
            'learning_success_rate': 0.0,
            'average_learning_strength': 0.0,
            'average_impact': 0.0,
            'average_coherence_change': 0.0,
            'average_information_gain': 0.0,
            'mode_statistics': {},
            'impact_distribution': {},
            'performance_trends': {}
        }
    
    def _calculate_mode_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by evolution type"""
        type_stats = {}
        
        for evo_type in EvolutionType:
            type_events = [e for e in self.evolution_history if e.evolution_type == evo_type]
            
            if type_events:
                total_impact = sum(e.calculate_evolution_impact() for e in type_events)
                significant_count = sum(1 for e in type_events if e.is_significant_evolution())
                
                type_stats[evo_type.value] = {
                    'count': len(type_events),
                    'significance_rate': significant_count / len(type_events),
                    'average_impact': total_impact / len(type_events),
                    'average_learning_strength': sum(e.learning_strength for e in type_events) / len(type_events)
                }
        
        return type_stats
    
    def _calculate_impact_distribution(self) -> Dict[str, int]:
        """Calculate impact grade distribution"""
        distribution = {'High': 0, 'Medium': 0, 'Low': 0, 'Minimal': 0}
        
        for event in self.evolution_history:
            grade = event.get_impact_grade()
            distribution[grade] += 1
        
        return distribution
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(self.evolution_history) < 10:
            return {'trend': 'insufficient_data'}
        
        # Split into first and second half
        mid_point = len(self.evolution_history) // 2
        first_half = self.evolution_history[:mid_point]
        second_half = self.evolution_history[mid_point:]
        
        # Calculate metrics for each half
        first_impact = sum(e.calculate_evolution_impact() for e in first_half) / len(first_half)
        second_impact = sum(e.calculate_evolution_impact() for e in second_half) / len(second_half)
        
        first_learning = sum(e.learning_strength for e in first_half) / len(first_half)
        second_learning = sum(e.learning_strength for e in second_half) / len(second_half)
        
        impact_trend = 'improving' if second_impact > first_impact else 'declining'
        learning_trend = 'improving' if second_learning > first_learning else 'declining'
        
        return {
            'impact_trend': impact_trend,
            'impact_change': second_impact - first_impact,
            'learning_trend': learning_trend,
            'learning_change': second_learning - first_learning,
            'first_half_impact': first_impact,
            'second_half_impact': second_impact
        }

# Utility functions
def create_evolution_statistics() -> EvolutionStatistics:
    """Create evolution statistics calculator"""
    return EvolutionStatistics()

def analyze_evolution_batch(events: List[EvolutionEvent]) -> Dict[str, Any]:
    """Analyze a batch of evolution events"""
    if not events:
        return {'error': 'no_events'}
    
    stats = EvolutionStatistics()
    for event in events:
        stats.add_evolution_event(event)
    
    return stats.get_comprehensive_statistics()

def get_evolution_summary(event: EvolutionEvent) -> str:
    """Get human-readable evolution summary"""
    impact = event.calculate_evolution_impact()
    grade = event.get_impact_grade()
    significant = "Significant" if event.is_significant_evolution() else "Minor"
    
    return (f"{significant} {event.evolution_type.value} evolution "
            f"(Impact: {impact:.3f}/{grade}, "
            f"Learning: {event.learning_strength:.3f}, "
            f"Coherence Δ: {event.coherence_change:+.3f}, "
            f"Duration: {event.evolution_duration*1000:.1f}ms)")

# Export statistics components
__all__ = [
    'EvolutionStatistics',
    'create_evolution_statistics',
    'analyze_evolution_batch',
    'get_evolution_summary'
]
