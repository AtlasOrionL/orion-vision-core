"""
🛡️ Information Conservation Law Core - Q1.2 Core Implementation

Core classes and data structures for Information Conservation Law (∇⋅J=0)
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 2
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

# Import Planck Information Unit
from .planck_information_unit import PlanckInformationUnit

# Conservation Event Types
class ConservationEventType(Enum):
    """Korunma olayı türleri"""
    TRANSFORMATION = "transformation"               # Bilgi dönüşümü
    INTERACTION = "interaction"                     # Etkileşim
    DECAY = "decay"                                 # Bozunma
    CREATION = "creation"                           # Yaratılma
    ANNIHILATION = "annihilation"                   # Yok olma

# Conservation Status
class ConservationStatus(Enum):
    """Korunma durumu"""
    CONSERVED = "conserved"                         # Korunmuş
    VIOLATED = "violated"                           # İhlal edilmiş
    UNCERTAIN = "uncertain"                         # Belirsiz
    CORRECTED = "corrected"                         # Düzeltilmiş

@dataclass
class ConservationEvent:
    """
    Conservation Event
    
    Bilgi korunma yasasının test edildiği olay kaydı.
    """
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: ConservationEventType = ConservationEventType.TRANSFORMATION
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Input/Output information
    input_units: List[PlanckInformationUnit] = field(default_factory=list)
    output_units: List[PlanckInformationUnit] = field(default_factory=list)
    
    # Conservation metrics
    input_total_mass: float = 0.0
    output_total_mass: float = 0.0
    conservation_error: float = 0.0
    conservation_status: ConservationStatus = ConservationStatus.UNCERTAIN
    
    # Process information
    process_name: str = ""
    process_id: str = ""
    
    # Correction information
    correction_applied: bool = False
    correction_method: str = ""
    z_boson_triggered: bool = False
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_conservation_metrics(self):
        """Calculate conservation metrics"""
        # Calculate input total
        self.input_total_mass = sum(unit.get_effective_mass() for unit in self.input_units)
        
        # Calculate output total
        self.output_total_mass = sum(unit.get_effective_mass() for unit in self.output_units)
        
        # Calculate conservation error
        self.conservation_error = abs(self.input_total_mass - self.output_total_mass)
        
        # Determine conservation status
        tolerance = 0.001  # 0.1% tolerance
        if self.conservation_error <= tolerance:
            self.conservation_status = ConservationStatus.CONSERVED
        else:
            self.conservation_status = ConservationStatus.VIOLATED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'input_units_count': len(self.input_units),
            'output_units_count': len(self.output_units),
            'input_total_mass': self.input_total_mass,
            'output_total_mass': self.output_total_mass,
            'conservation_error': self.conservation_error,
            'conservation_status': self.conservation_status.value,
            'process_name': self.process_name,
            'process_id': self.process_id,
            'correction_applied': self.correction_applied,
            'correction_method': self.correction_method,
            'z_boson_triggered': self.z_boson_triggered,
            'metadata': self.metadata
        }

class ZBosonTrigger:
    """
    Z Boson Trigger
    
    Bilgi dekohaeransı (conservation violation) durumunda tetiklenen sistem.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.trigger_count = 0
        self.trigger_history: List[Dict[str, Any]] = []
        
    def trigger_decoherence_signal(self, 
                                  conservation_event: ConservationEvent,
                                  severity: str = "medium") -> str:
        """Trigger Z Boson decoherence signal"""
        
        trigger_id = str(uuid.uuid4())
        trigger_time = datetime.now()
        
        trigger_data = {
            'trigger_id': trigger_id,
            'timestamp': trigger_time.isoformat(),
            'conservation_event_id': conservation_event.event_id,
            'conservation_error': conservation_event.conservation_error,
            'severity': severity,
            'process_name': conservation_event.process_name,
            'input_mass': conservation_event.input_total_mass,
            'output_mass': conservation_event.output_total_mass
        }
        
        self.trigger_history.append(trigger_data)
        self.trigger_count += 1
        
        # Mark event as having Z Boson triggered
        conservation_event.z_boson_triggered = True
        
        self.logger.warning(f"⚡ Z Boson triggered: {trigger_id[:8]}... "
                          f"(error: {conservation_event.conservation_error:.6f}, "
                          f"severity: {severity})")
        
        return trigger_id
    
    def get_trigger_statistics(self) -> Dict[str, Any]:
        """Get Z Boson trigger statistics"""
        if not self.trigger_history:
            return {
                'total_triggers': 0,
                'recent_triggers': 0,
                'average_error': 0.0,
                'severity_distribution': {}
            }
        
        # Recent triggers (last hour)
        recent_time = datetime.now().timestamp() - 3600
        recent_triggers = [
            t for t in self.trigger_history 
            if datetime.fromisoformat(t['timestamp']).timestamp() > recent_time
        ]
        
        # Average error
        total_error = sum(t['conservation_error'] for t in self.trigger_history)
        avg_error = total_error / len(self.trigger_history)
        
        # Severity distribution
        severity_counts = {}
        for trigger in self.trigger_history:
            severity = trigger['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_triggers': self.trigger_count,
            'recent_triggers': len(recent_triggers),
            'average_error': avg_error,
            'severity_distribution': severity_counts,
            'last_trigger': self.trigger_history[-1] if self.trigger_history else None
        }

# Export core components
__all__ = [
    'ConservationEventType',
    'ConservationStatus',
    'ConservationEvent',
    'ZBosonTrigger'
]
