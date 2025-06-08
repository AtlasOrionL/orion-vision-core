"""
🔥 Optimizer Statistics - Q5.2 Statistics Component

Statistics and utilities for Information Thermodynamics Optimizer
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q5.2 Information Thermodynamics Optimizer
Priority: CRITICAL - Modular Design Refactoring Phase 9
"""

from typing import Dict, List, Any

# Import core components
from .thermodynamics_core import OptimizationResult, ThermodynamicState, OptimizationStrategy

class OptimizerStatistics:
    """
    Optimizer Statistics Calculator
    
    Provides comprehensive statistics for optimization results.
    """
    
    def __init__(self):
        self.optimization_history: List[OptimizationResult] = []
        self.state_history: List[ThermodynamicState] = []
    
    def add_optimization_result(self, result: OptimizationResult):
        """Add optimization result to statistics"""
        self.optimization_history.append(result)
        
        # Add states to history
        if result.initial_state:
            self.state_history.append(result.initial_state)
        if result.final_state:
            self.state_history.append(result.final_state)
        
        # Limit history size
        if len(self.optimization_history) > 1000:
            self.optimization_history = self.optimization_history[-500:]
        if len(self.state_history) > 2000:
            self.state_history = self.state_history[-1000:]
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        if not self.optimization_history:
            return self._empty_statistics()
        
        # Basic counts
        total_optimizations = len(self.optimization_history)
        successful_optimizations = sum(1 for r in self.optimization_history if r.success_rate > 0.5)
        convergent_optimizations = sum(1 for r in self.optimization_history if r.convergence_achieved)
        
        # Performance metrics
        total_improvement = sum(r.calculate_overall_improvement() for r in self.optimization_history)
        average_improvement = total_improvement / total_optimizations
        
        # Strategy-specific statistics
        strategy_stats = self._calculate_strategy_statistics()
        
        # Efficiency metrics
        efficiency_stats = self._calculate_efficiency_statistics()
        
        # Performance trends
        performance_trends = self._calculate_performance_trends()
        
        return {
            'total_optimizations': total_optimizations,
            'successful_optimizations': successful_optimizations,
            'success_rate': successful_optimizations / total_optimizations,
            'convergent_optimizations': convergent_optimizations,
            'convergence_rate': convergent_optimizations / total_optimizations,
            'average_improvement': average_improvement,
            'strategy_statistics': strategy_stats,
            'efficiency_statistics': efficiency_stats,
            'performance_trends': performance_trends
        }
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """Return empty statistics when no optimizations available"""
        return {
            'total_optimizations': 0,
            'success_rate': 0.0,
            'convergence_rate': 0.0,
            'average_improvement': 0.0,
            'strategy_statistics': {},
            'efficiency_statistics': {},
            'performance_trends': {}
        }
    
    def _calculate_strategy_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by optimization strategy"""
        strategy_stats = {}
        
        for strategy in OptimizationStrategy:
            strategy_results = [r for r in self.optimization_history if r.strategy == strategy]
            
            if strategy_results:
                total_improvement = sum(r.calculate_overall_improvement() for r in strategy_results)
                successful_count = sum(1 for r in strategy_results if r.success_rate > 0.5)
                
                strategy_stats[strategy.value] = {
                    'count': len(strategy_results),
                    'success_rate': successful_count / len(strategy_results),
                    'average_improvement': total_improvement / len(strategy_results),
                    'average_entropy_reduction': sum(r.entropy_reduction for r in strategy_results) / len(strategy_results),
                    'average_information_gain': sum(r.information_gain for r in strategy_results) / len(strategy_results),
                    'average_coherence_improvement': sum(r.coherence_improvement for r in strategy_results) / len(strategy_results)
                }
        
        return strategy_stats
    
    def _calculate_efficiency_statistics(self) -> Dict[str, Any]:
        """Calculate efficiency statistics"""
        if not self.state_history:
            return {}
        
        # Calculate average efficiency metrics
        avg_information_density = sum(s.information_density for s in self.state_history) / len(self.state_history)
        avg_entropy = sum(s.entropy for s in self.state_history) / len(self.state_history)
        avg_coherence = sum(s.coherence_factor for s in self.state_history) / len(self.state_history)
        avg_efficiency = sum(s.calculate_information_efficiency() for s in self.state_history) / len(self.state_history)
        
        # Efficiency distribution
        efficiency_grades = {}
        for state in self.state_history:
            grade = state.get_efficiency_grade()
            efficiency_grades[grade] = efficiency_grades.get(grade, 0) + 1
        
        return {
            'average_information_density': avg_information_density,
            'average_entropy': avg_entropy,
            'average_coherence': avg_coherence,
            'average_efficiency': avg_efficiency,
            'efficiency_distribution': efficiency_grades
        }
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(self.optimization_history) < 10:
            return {'trend': 'insufficient_data'}
        
        # Split into first and second half
        mid_point = len(self.optimization_history) // 2
        first_half = self.optimization_history[:mid_point]
        second_half = self.optimization_history[mid_point:]
        
        # Calculate metrics for each half
        first_improvement = sum(r.calculate_overall_improvement() for r in first_half) / len(first_half)
        second_improvement = sum(r.calculate_overall_improvement() for r in second_half) / len(second_half)
        
        first_success_rate = sum(1 for r in first_half if r.success_rate > 0.5) / len(first_half)
        second_success_rate = sum(1 for r in second_half if r.success_rate > 0.5) / len(second_half)
        
        improvement_trend = 'improving' if second_improvement > first_improvement else 'declining'
        success_trend = 'improving' if second_success_rate > first_success_rate else 'declining'
        
        return {
            'improvement_trend': improvement_trend,
            'improvement_change': second_improvement - first_improvement,
            'success_trend': success_trend,
            'success_rate_change': second_success_rate - first_success_rate,
            'first_half_improvement': first_improvement,
            'second_half_improvement': second_improvement
        }

# Utility functions
def get_optimizer_statistics(optimizer) -> Dict[str, Any]:
    """Get comprehensive optimizer statistics"""
    if not optimizer.optimization_results:
        return {
            'total_optimizations': 0,
            'success_rate': 0.0,
            'average_improvement': 0.0,
            'current_system_entropy': 0.0
        }
    
    # Calculate statistics
    total_improvement = sum(r.calculate_overall_improvement() for r in optimizer.optimization_results)
    avg_improvement = total_improvement / len(optimizer.optimization_results)
    success_rate = optimizer.successful_optimizations / optimizer.total_optimizations if optimizer.total_optimizations > 0 else 0.0
    
    # Current system state
    current_entropy = optimizer.current_state.entropy if optimizer.current_state else 0.0
    current_efficiency = optimizer.current_state.calculate_information_efficiency() if optimizer.current_state else 0.0
    
    return {
        'total_optimizations': optimizer.total_optimizations,
        'successful_optimizations': optimizer.successful_optimizations,
        'success_rate': success_rate,
        'average_improvement': avg_improvement,
        'current_system_entropy': current_entropy,
        'current_system_efficiency': current_efficiency,
        'convergence_threshold': optimizer.convergence_threshold,
        'default_strategy': optimizer.default_strategy.value
    }

def create_optimizer_statistics() -> OptimizerStatistics:
    """Create optimizer statistics calculator"""
    return OptimizerStatistics()

def analyze_optimization_batch(results: List[OptimizationResult]) -> Dict[str, Any]:
    """Analyze a batch of optimization results"""
    if not results:
        return {'error': 'no_results'}
    
    stats = OptimizerStatistics()
    for result in results:
        stats.add_optimization_result(result)
    
    return stats.get_comprehensive_statistics()

def get_optimization_summary(result: OptimizationResult) -> str:
    """Get human-readable optimization summary"""
    improvement = result.calculate_overall_improvement()
    grade = result.get_improvement_grade()
    convergence = "Converged" if result.convergence_achieved else "Not converged"
    
    return (f"{result.strategy.value} optimization "
            f"(Improvement: {improvement:.3f}/{grade}, "
            f"Entropy Δ: {result.entropy_reduction:+.3f}, "
            f"Info gain: {result.information_gain:+.3f}, "
            f"{convergence}, Duration: {result.optimization_time*1000:.1f}ms)")

def get_thermodynamic_summary(state: ThermodynamicState) -> str:
    """Get human-readable thermodynamic state summary"""
    efficiency = state.calculate_information_efficiency()
    grade = state.get_efficiency_grade()
    
    return (f"Thermodynamic state "
            f"(T: {state.temperature:.3f}, "
            f"S: {state.entropy:.3f}, "
            f"ρ_info: {state.information_density:.3f}, "
            f"Efficiency: {efficiency:.3f}/{grade}, "
            f"Particles: {state.particle_count})")

# Export statistics components
__all__ = [
    'OptimizerStatistics',
    'get_optimizer_statistics',
    'create_optimizer_statistics',
    'analyze_optimization_batch',
    'get_optimization_summary',
    'get_thermodynamic_summary'
]
