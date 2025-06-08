"""
🛡️ Conservation Validator - Q1.2 Validator Component

Validation and correction system for Information Conservation Law
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q1.2 Information Conservation Law
Priority: CRITICAL - Modular Design Refactoring Phase 2
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Callable

# Import core components
from .conservation_law_core import (
    ConservationEvent, ConservationEventType, ConservationStatus, ZBosonTrigger
)
from .planck_information_unit import PlanckInformationUnit

class InformationConservationLaw:
    """
    Information Conservation Law (∇⋅J=0)
    
    Bilgi korunma yasasının uygulanması ve ihlallerin tespiti.
    """
    
    def __init__(self, tolerance: float = 0.001):
        self.logger = logging.getLogger(__name__)
        self.tolerance = tolerance
        
        # Conservation tracking
        self.conservation_events: List[ConservationEvent] = []
        self.violation_count = 0
        self.correction_count = 0
        
        # Z Boson trigger system
        self.z_boson_trigger = ZBosonTrigger()
        
        # Correction methods
        self.correction_methods: Dict[str, Callable] = {
            'normalize': self._normalize_correction,
            'redistribute': self._redistribute_correction,
            'compensate': self._compensate_correction
        }
        
        self.logger.info("🛡️ InformationConservationLaw initialized - Q1.2 Implementation")
    
    def validate_process(self,
                        input_units: List[PlanckInformationUnit],
                        output_units: List[PlanckInformationUnit],
                        process_name: str = "",
                        process_id: str = "",
                        event_type: ConservationEventType = ConservationEventType.TRANSFORMATION) -> ConservationEvent:
        """Validate information conservation for a process"""
        
        # Create conservation event
        event = ConservationEvent(
            event_type=event_type,
            input_units=input_units.copy(),
            output_units=output_units.copy(),
            process_name=process_name,
            process_id=process_id
        )
        
        # Calculate conservation metrics
        event.calculate_conservation_metrics()
        
        # Check for violation
        if event.conservation_status == ConservationStatus.VIOLATED:
            self.violation_count += 1
            
            # Determine severity
            error_ratio = event.conservation_error / max(event.input_total_mass, 0.001)
            if error_ratio > 0.1:
                severity = "critical"
            elif error_ratio > 0.05:
                severity = "high"
            elif error_ratio > 0.01:
                severity = "medium"
            else:
                severity = "low"
            
            # Trigger Z Boson
            trigger_id = self.z_boson_trigger.trigger_decoherence_signal(event, severity)
            
            self.logger.warning(f"⚠️ Conservation violation detected: {event.event_id[:8]}... "
                              f"(error: {event.conservation_error:.6f}, severity: {severity})")
            
            # Attempt correction
            if severity in ["critical", "high"]:
                self._attempt_correction(event)
        
        else:
            self.logger.debug(f"✅ Conservation verified: {event.event_id[:8]}... "
                            f"(error: {event.conservation_error:.6f})")
        
        # Store event
        self.conservation_events.append(event)
        
        # Limit event history
        if len(self.conservation_events) > 1000:
            self.conservation_events = self.conservation_events[-500:]
        
        return event
    
    def _attempt_correction(self, event: ConservationEvent) -> bool:
        """Attempt to correct conservation violation"""
        try:
            # Try different correction methods
            for method_name, method_func in self.correction_methods.items():
                if method_func(event):
                    event.correction_applied = True
                    event.correction_method = method_name
                    event.conservation_status = ConservationStatus.CORRECTED
                    self.correction_count += 1
                    
                    self.logger.info(f"✅ Conservation corrected using {method_name}: "
                                   f"{event.event_id[:8]}...")
                    return True
            
            self.logger.error(f"❌ Failed to correct conservation violation: "
                            f"{event.event_id[:8]}...")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Correction attempt failed: {e}")
            return False
    
    def _normalize_correction(self, event: ConservationEvent) -> bool:
        """Normalize output units to match input total"""
        try:
            if not event.output_units or event.input_total_mass == 0:
                return False
            
            # Calculate normalization factor
            normalization_factor = event.input_total_mass / event.output_total_mass
            
            # Apply normalization to output units
            for unit in event.output_units:
                unit.information_content *= normalization_factor
                unit._determine_quality_level()
            
            # Recalculate metrics
            event.calculate_conservation_metrics()
            
            return event.conservation_error <= self.tolerance
            
        except Exception as e:
            self.logger.error(f"❌ Normalize correction failed: {e}")
            return False
    
    def _redistribute_correction(self, event: ConservationEvent) -> bool:
        """Redistribute mass among output units"""
        try:
            if not event.output_units:
                return False
            
            # Calculate missing mass
            missing_mass = event.input_total_mass - event.output_total_mass
            mass_per_unit = missing_mass / len(event.output_units)
            
            # Redistribute mass
            for unit in event.output_units:
                unit.information_content += mass_per_unit
                unit._determine_quality_level()
            
            # Recalculate metrics
            event.calculate_conservation_metrics()
            
            return event.conservation_error <= self.tolerance
            
        except Exception as e:
            self.logger.error(f"❌ Redistribute correction failed: {e}")
            return False
    
    def _compensate_correction(self, event: ConservationEvent) -> bool:
        """Create compensating unit for missing mass"""
        try:
            # Calculate missing mass
            missing_mass = event.input_total_mass - event.output_total_mass
            
            if abs(missing_mass) <= self.tolerance:
                return True
            
            # Create compensating unit
            if missing_mass > 0:
                # Create unit with missing mass
                compensating_unit = PlanckInformationUnit(
                    coherence_factor=0.5
                )
                compensating_unit.information_content = missing_mass
                compensating_unit.metadata.update({'compensation': True, 'original_event': event.event_id})
                compensating_unit._determine_quality_level()
                event.output_units.append(compensating_unit)
            else:
                # Remove excess mass from largest unit
                if event.output_units:
                    largest_unit = max(event.output_units, key=lambda u: u.information_content)
                    largest_unit.information_content += missing_mass  # missing_mass is negative
                    largest_unit._determine_quality_level()
            
            # Recalculate metrics
            event.calculate_conservation_metrics()
            
            return event.conservation_error <= self.tolerance
            
        except Exception as e:
            self.logger.error(f"❌ Compensate correction failed: {e}")
            return False
    
    def get_conservation_statistics(self) -> Dict[str, Any]:
        """Get conservation law statistics"""
        if not self.conservation_events:
            return {
                'total_events': 0,
                'violation_rate': 0.0,
                'correction_rate': 0.0,
                'average_error': 0.0,
                'z_boson_stats': self.z_boson_trigger.get_trigger_statistics()
            }
        
        # Calculate statistics
        total_events = len(self.conservation_events)
        violations = sum(1 for e in self.conservation_events 
                        if e.conservation_status == ConservationStatus.VIOLATED)
        corrections = sum(1 for e in self.conservation_events 
                         if e.correction_applied)
        
        violation_rate = violations / total_events
        correction_rate = corrections / violations if violations > 0 else 0.0
        
        # Average error
        total_error = sum(e.conservation_error for e in self.conservation_events)
        average_error = total_error / total_events
        
        # Recent events (last hour)
        recent_time = datetime.now().timestamp() - 3600
        recent_events = [
            e for e in self.conservation_events 
            if e.timestamp.timestamp() > recent_time
        ]
        
        return {
            'total_events': total_events,
            'violation_count': self.violation_count,
            'correction_count': self.correction_count,
            'violation_rate': violation_rate,
            'correction_rate': correction_rate,
            'average_error': average_error,
            'recent_events': len(recent_events),
            'tolerance': self.tolerance,
            'z_boson_stats': self.z_boson_trigger.get_trigger_statistics()
        }

# Utility function
def create_conservation_law(tolerance: float = 0.001) -> InformationConservationLaw:
    """Create Information Conservation Law system"""
    return InformationConservationLaw(tolerance)

# Export validator components
__all__ = [
    'InformationConservationLaw',
    'create_conservation_law'
]
