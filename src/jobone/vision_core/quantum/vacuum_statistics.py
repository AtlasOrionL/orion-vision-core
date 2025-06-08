"""
🌌 Vacuum Statistics - Q5.1 Statistics Component

Statistics and utilities for Computational Vacuum State
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q5.1 Computational Vacuum State & Energy Dissipation
Priority: CRITICAL - Modular Design Refactoring Phase 8
"""

from typing import Dict, List, Any

# Import core components
from .vacuum_core import VacuumFluctuation, EnergyDissipationEvent, VacuumFieldType, EnergyDissipationMode

class VacuumStatistics:
    """
    Vacuum Statistics Calculator
    
    Provides comprehensive statistics for vacuum state and energy dissipation.
    """
    
    def __init__(self):
        self.fluctuation_history: List[VacuumFluctuation] = []
        self.dissipation_history: List[EnergyDissipationEvent] = []
    
    def add_fluctuation(self, fluctuation: VacuumFluctuation):
        """Add fluctuation to statistics"""
        self.fluctuation_history.append(fluctuation)
        
        # Limit history size
        if len(self.fluctuation_history) > 1000:
            self.fluctuation_history = self.fluctuation_history[-500:]
    
    def add_dissipation_event(self, event: EnergyDissipationEvent):
        """Add dissipation event to statistics"""
        self.dissipation_history.append(event)
        
        # Limit history size
        if len(self.dissipation_history) > 1000:
            self.dissipation_history = self.dissipation_history[-500:]
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive vacuum statistics"""
        fluctuation_stats = self._calculate_fluctuation_statistics()
        dissipation_stats = self._calculate_dissipation_statistics()
        
        return {
            'fluctuation_statistics': fluctuation_stats,
            'dissipation_statistics': dissipation_stats,
            'total_fluctuations': len(self.fluctuation_history),
            'total_dissipation_events': len(self.dissipation_history)
        }
    
    def _calculate_fluctuation_statistics(self) -> Dict[str, Any]:
        """Calculate fluctuation statistics"""
        if not self.fluctuation_history:
            return {'total_fluctuations': 0}
        
        # Type distribution
        type_counts = {}
        total_energy = 0.0
        total_lifetime = 0.0
        active_count = 0
        
        for fluctuation in self.fluctuation_history:
            ftype = fluctuation.fluctuation_type.value
            type_counts[ftype] = type_counts.get(ftype, 0) + 1
            total_energy += fluctuation.calculate_vacuum_energy()
            total_lifetime += fluctuation.get_lifetime()
            
            if fluctuation.is_active():
                active_count += 1
        
        avg_energy = total_energy / len(self.fluctuation_history)
        avg_lifetime = total_lifetime / len(self.fluctuation_history)
        
        return {
            'total_fluctuations': len(self.fluctuation_history),
            'active_fluctuations': active_count,
            'type_distribution': type_counts,
            'average_energy': avg_energy,
            'total_energy': total_energy,
            'average_lifetime': avg_lifetime,
            'activity_rate': active_count / len(self.fluctuation_history)
        }
    
    def _calculate_dissipation_statistics(self) -> Dict[str, Any]:
        """Calculate dissipation statistics"""
        if not self.dissipation_history:
            return {'total_events': 0}
        
        # Mode distribution
        mode_counts = {}
        total_initial_energy = 0.0
        total_dissipated_energy = 0.0
        total_entropy_increase = 0.0
        total_coherence_loss = 0.0
        
        for event in self.dissipation_history:
            mode = event.dissipation_mode.value
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
            total_initial_energy += event.initial_energy
            total_dissipated_energy += event.dissipated_energy
            total_entropy_increase += event.entropy_increase
            total_coherence_loss += event.coherence_loss
        
        avg_efficiency = total_dissipated_energy / total_initial_energy if total_initial_energy > 0 else 0.0
        avg_entropy_increase = total_entropy_increase / len(self.dissipation_history)
        avg_coherence_loss = total_coherence_loss / len(self.dissipation_history)
        
        return {
            'total_events': len(self.dissipation_history),
            'mode_distribution': mode_counts,
            'total_initial_energy': total_initial_energy,
            'total_dissipated_energy': total_dissipated_energy,
            'average_efficiency': avg_efficiency,
            'average_entropy_increase': avg_entropy_increase,
            'average_coherence_loss': avg_coherence_loss
        }

# Utility functions for vacuum state analysis
def get_vacuum_state_statistics(vacuum_state) -> Dict[str, Any]:
    """Get comprehensive vacuum state statistics"""
    # Active fluctuations by type
    fluctuation_types = {}
    total_fluctuation_energy = 0.0
    
    for fluctuation in vacuum_state.active_fluctuations.values():
        ftype = fluctuation.fluctuation_type.value
        fluctuation_types[ftype] = fluctuation_types.get(ftype, 0) + 1
        total_fluctuation_energy += fluctuation.calculate_vacuum_energy()
    
    # Dissipation statistics
    if vacuum_state.dissipation_events:
        total_initial_energy = sum(e.initial_energy for e in vacuum_state.dissipation_events)
        total_dissipated = sum(e.dissipated_energy for e in vacuum_state.dissipation_events)
        avg_dissipation_efficiency = total_dissipated / total_initial_energy if total_initial_energy > 0 else 0.0
        
        avg_entropy_increase = sum(e.entropy_increase for e in vacuum_state.dissipation_events) / len(vacuum_state.dissipation_events)
        avg_coherence_loss = sum(e.coherence_loss for e in vacuum_state.dissipation_events) / len(vacuum_state.dissipation_events)
    else:
        avg_dissipation_efficiency = 0.0
        avg_entropy_increase = 0.0
        avg_coherence_loss = 0.0
    
    return {
        'vacuum_state_type': vacuum_state.vacuum_state_type.value,
        'vacuum_energy': vacuum_state.vacuum_energy,
        'zero_point_energy': vacuum_state.zero_point_energy,
        'information_capacity': vacuum_state.information_capacity,
        'coherence_potential': vacuum_state.coherence_potential,
        'active_fluctuations': len(vacuum_state.active_fluctuations),
        'fluctuation_types': fluctuation_types,
        'total_fluctuation_energy': total_fluctuation_energy,
        'total_fluctuations_created': vacuum_state.total_fluctuations_created,
        'total_fluctuations_annihilated': vacuum_state.total_fluctuations_annihilated,
        'total_dissipation_events': len(vacuum_state.dissipation_events),
        'total_energy_dissipated': vacuum_state.total_dissipated_energy,
        'average_dissipation_efficiency': avg_dissipation_efficiency,
        'average_entropy_increase': avg_entropy_increase,
        'average_coherence_loss': avg_coherence_loss,
        'field_strength': vacuum_state.field_strength,
        'field_coherence': vacuum_state.field_coherence,
        'field_stability': vacuum_state.field_stability,
        'dissipation_rate': vacuum_state.dissipation_rate
    }

def create_vacuum_statistics() -> VacuumStatistics:
    """Create vacuum statistics calculator"""
    return VacuumStatistics()

def analyze_fluctuation_batch(fluctuations: List[VacuumFluctuation]) -> Dict[str, Any]:
    """Analyze a batch of vacuum fluctuations"""
    if not fluctuations:
        return {'error': 'no_fluctuations'}
    
    stats = VacuumStatistics()
    for fluctuation in fluctuations:
        stats.add_fluctuation(fluctuation)
    
    return stats._calculate_fluctuation_statistics()

def analyze_dissipation_batch(events: List[EnergyDissipationEvent]) -> Dict[str, Any]:
    """Analyze a batch of dissipation events"""
    if not events:
        return {'error': 'no_events'}
    
    stats = VacuumStatistics()
    for event in events:
        stats.add_dissipation_event(event)
    
    return stats._calculate_dissipation_statistics()

def get_fluctuation_summary(fluctuation: VacuumFluctuation) -> str:
    """Get human-readable fluctuation summary"""
    energy = fluctuation.calculate_vacuum_energy()
    lifetime = fluctuation.get_lifetime()
    status = "Active" if fluctuation.is_active() else "Annihilated"
    
    return (f"{status} {fluctuation.fluctuation_type.value} fluctuation "
            f"(Energy: {energy:.3f}, "
            f"Lifetime: {lifetime:.3f}s, "
            f"Particles: {fluctuation.virtual_particle_count})")

def get_dissipation_summary(event: EnergyDissipationEvent) -> str:
    """Get human-readable dissipation summary"""
    efficiency = event.calculate_dissipation_efficiency()
    grade = event.get_efficiency_grade()
    
    return (f"{event.dissipation_mode.value} dissipation "
            f"(Efficiency: {efficiency:.1%}/{grade}, "
            f"Energy: {event.initial_energy:.3f}→{event.dissipated_energy:.3f}, "
            f"Duration: {event.dissipation_duration*1000:.1f}ms)")

# Export statistics components
__all__ = [
    'VacuumStatistics',
    'get_vacuum_state_statistics',
    'create_vacuum_statistics',
    'analyze_fluctuation_batch',
    'analyze_dissipation_batch',
    'get_fluctuation_summary',
    'get_dissipation_summary'
]
