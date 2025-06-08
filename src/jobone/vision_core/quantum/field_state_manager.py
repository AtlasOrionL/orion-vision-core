"""
🔮 Field State Manager - Q05.1.1 Component

Kuantum alan durumu yönetimi ve gözlemci etkisi.
ALT_LAS Quantum Mind OS ile entegre çalışır.

Bu modül Q05.1.1 görevinin üçüncü parçasıdır:
- Field state management ✅
- State transition handling
- Quantum observer effects
- Coherence management

Author: Orion Vision Core Team
Sprint: Q05.1.1 - QFD Temel Altyapısı
Status: IMPLEMENTED
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Tuple
import uuid
import json

from .qfd_base import QFDBase, QFDConfig, QuantumEntity, EntityType, QFDException
from .quantum_field import QuantumState, QuantumField, FieldType

# State Transition Types
class TransitionType(Enum):
    """Durum geçiş türleri"""
    SPONTANEOUS = "spontaneous"        # Kendiliğinden geçiş
    INDUCED = "induced"                # Uyarılmış geçiş
    MEASUREMENT = "measurement"        # Ölçüm kaynaklı
    DECOHERENCE = "decoherence"       # Dekoherans
    ENTANGLEMENT = "entanglement"     # Dolaşıklık
    ALT_LAS_TRIGGER = "alt_las_trigger"  # ALT_LAS tetiklemesi

# Observer Types
class ObserverType(Enum):
    """Gözlemci türleri"""
    PASSIVE = "passive"                # Pasif gözlem
    ACTIVE = "active"                  # Aktif müdahale
    QUANTUM = "quantum"                # Kuantum gözlemci
    ALT_LAS = "alt_las"               # ALT_LAS gözlemci
    EXTERNAL = "external"              # Dış sistem

@dataclass
class StateTransition:
    """Durum geçişi kaydı"""
    
    transition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Transition details
    from_state: str = ""
    to_state: str = ""
    transition_type: TransitionType = TransitionType.SPONTANEOUS
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0  # seconds
    
    # Quantum properties
    probability: float = 1.0
    coherence_before: float = 1.0
    coherence_after: float = 1.0
    
    # Observer information
    observer_id: Optional[str] = None
    observer_type: Optional[ObserverType] = None
    
    # ALT_LAS integration
    alt_las_seed_before: Optional[str] = None
    alt_las_seed_after: Optional[str] = None
    atlas_memory_ref: Optional[str] = None
    
    # Additional data
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'transition_id': self.transition_id,
            'from_state': self.from_state,
            'to_state': self.to_state,
            'transition_type': self.transition_type.value,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'probability': self.probability,
            'coherence_before': self.coherence_before,
            'coherence_after': self.coherence_after,
            'observer_id': self.observer_id,
            'observer_type': self.observer_type.value if self.observer_type else None,
            'alt_las_seed_before': self.alt_las_seed_before,
            'alt_las_seed_after': self.alt_las_seed_after,
            'atlas_memory_ref': self.atlas_memory_ref,
            'metadata': self.metadata
        }

@dataclass
class QuantumObserver:
    """Kuantum gözlemci"""
    
    observer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    observer_type: ObserverType = ObserverType.PASSIVE
    
    # Observer properties
    name: str = "Unknown Observer"
    measurement_strength: float = 1.0
    decoherence_rate: float = 0.1
    
    # Observation history
    observations_made: int = 0
    last_observation: Optional[datetime] = None
    
    # ALT_LAS integration
    alt_las_connected: bool = False
    quantum_seed: Optional[str] = None
    
    def observe(self, quantum_state: QuantumState) -> StateTransition:
        """Perform quantum observation"""
        start_time = datetime.now()
        
        # Record initial state
        initial_coherence = quantum_state.coherence
        
        # Apply observer effect
        if self.observer_type == ObserverType.ACTIVE:
            # Active observation causes more decoherence
            quantum_state.coherence *= (1.0 - self.decoherence_rate * self.measurement_strength)
        elif self.observer_type == ObserverType.PASSIVE:
            # Passive observation causes minimal decoherence
            quantum_state.coherence *= (1.0 - self.decoherence_rate * 0.1)
        
        # Ensure coherence doesn't go below 0
        quantum_state.coherence = max(0.0, quantum_state.coherence)
        
        # Update observation count
        self.observations_made += 1
        self.last_observation = datetime.now()
        
        # Create transition record
        transition = StateTransition(
            from_state="observed_state",
            to_state="post_observation_state",
            transition_type=TransitionType.MEASUREMENT,
            timestamp=start_time,
            duration=(datetime.now() - start_time).total_seconds(),
            probability=1.0,
            coherence_before=initial_coherence,
            coherence_after=quantum_state.coherence,
            observer_id=self.observer_id,
            observer_type=self.observer_type,
            metadata={
                'measurement_strength': self.measurement_strength,
                'decoherence_applied': self.decoherence_rate
            }
        )
        
        return transition

class FieldStateManager(QFDBase):
    """
    Kuantum alan durumu yöneticisi
    
    Quantum field state'lerini yönetir, geçişleri takip eder,
    gözlemci etkilerini simüle eder ve ALT_LAS ile entegre çalışır.
    """
    
    def __init__(self, config: Optional[QFDConfig] = None):
        super().__init__(config)
        
        # State management
        self.managed_fields: Dict[str, QuantumField] = {}
        self.state_history: List[StateTransition] = []
        self.active_observers: Dict[str, QuantumObserver] = {}
        
        # Transition rules
        self.transition_rules: Dict[str, Callable] = {}
        self.auto_transitions_enabled = True
        
        # Performance tracking
        self.total_transitions = 0
        self.successful_transitions = 0
        self.failed_transitions = 0
        
        # ALT_LAS integration
        self.alt_las_integration_active = False
        self.quantum_seed_manager = None
        
        # Threading
        self._state_lock = threading.Lock()
        self._observer_lock = threading.Lock()
        
        self.logger.info("🔮 FieldStateManager initialized")
    
    def initialize(self) -> bool:
        """Initialize field state manager"""
        try:
            # Validate configuration
            if not self.validate_config():
                return False
            
            # Setup ALT_LAS integration
            if self.config.alt_las_integration:
                self._setup_alt_las_integration()
            
            # Register default transition rules
            self._register_default_transition_rules()
            
            # Create default observer
            self._create_default_observer()
            
            self.initialized = True
            self.active = True
            
            self.logger.info("✅ FieldStateManager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ FieldStateManager initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown field state manager"""
        try:
            self.active = False
            self.auto_transitions_enabled = False
            
            # Clear all managed data
            with self._state_lock:
                self.managed_fields.clear()
                self.state_history.clear()
            
            with self._observer_lock:
                self.active_observers.clear()
            
            self.logger.info("🔴 FieldStateManager shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ FieldStateManager shutdown failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status"""
        with self._state_lock, self._observer_lock:
            return {
                'initialized': self.initialized,
                'active': self.active,
                'managed_fields': len(self.managed_fields),
                'active_observers': len(self.active_observers),
                'total_transitions': self.total_transitions,
                'successful_transitions': self.successful_transitions,
                'failed_transitions': self.failed_transitions,
                'success_rate': (self.successful_transitions / max(1, self.total_transitions)) * 100,
                'alt_las_integration': self.alt_las_integration_active,
                'auto_transitions': self.auto_transitions_enabled,
                'state_history_size': len(self.state_history)
            }
    
    def register_field(self, field: QuantumField) -> bool:
        """Register a quantum field for management"""
        try:
            with self._state_lock:
                self.managed_fields[field.field_id] = field
                self.logger.info(f"✅ Registered field: {field.field_id}")
                return True
        except Exception as e:
            self.logger.error(f"❌ Field registration failed: {e}")
            return False
    
    def register_observer(self, observer: QuantumObserver) -> bool:
        """Register a quantum observer"""
        try:
            with self._observer_lock:
                self.active_observers[observer.observer_id] = observer
                self.logger.info(f"👁️ Registered observer: {observer.name}")
                return True
        except Exception as e:
            self.logger.error(f"❌ Observer registration failed: {e}")
            return False
    
    def trigger_state_transition(self, field_id: str, from_state: str, to_state: str,
                                transition_type: TransitionType = TransitionType.INDUCED,
                                observer_id: Optional[str] = None) -> Optional[StateTransition]:
        """Trigger a state transition"""
        try:
            start_time = datetime.now()
            
            with self._state_lock:
                if field_id not in self.managed_fields:
                    raise QFDException(f"Field {field_id} not managed")
                
                field = self.managed_fields[field_id]
                
                # Check if states exist
                if from_state not in field.field_states:
                    raise QFDException(f"From state {from_state} not found")
                
                # Get observer if specified
                observer = None
                if observer_id and observer_id in self.active_observers:
                    observer = self.active_observers[observer_id]
                
                # Record initial state
                initial_state = field.field_states[from_state]
                initial_coherence = initial_state.coherence
                
                # Apply transition
                if to_state not in field.field_states:
                    # Create new state if it doesn't exist
                    field.field_states[to_state] = QuantumState(
                        amplitudes=[1.0 + 0j],
                        basis_states=[f"|{to_state}⟩"]
                    )
                
                # Apply observer effect if present
                if observer:
                    observer.observe(initial_state)
                
                # Create transition record
                transition = StateTransition(
                    from_state=from_state,
                    to_state=to_state,
                    transition_type=transition_type,
                    timestamp=start_time,
                    duration=(datetime.now() - start_time).total_seconds(),
                    probability=1.0,
                    coherence_before=initial_coherence,
                    coherence_after=initial_state.coherence,
                    observer_id=observer_id,
                    observer_type=observer.observer_type if observer else None
                )
                
                # Record transition
                self.state_history.append(transition)
                self.total_transitions += 1
                self.successful_transitions += 1
                
                # Update field metrics
                field.state_transitions += 1
                
                self.logger.info(f"🔄 State transition: {from_state} → {to_state} in {field_id}")
                return transition
                
        except Exception as e:
            self.failed_transitions += 1
            self.logger.error(f"❌ State transition failed: {e}")
            return None
    
    def get_field_state_info(self, field_id: str) -> Optional[Dict[str, Any]]:
        """Get field state information"""
        with self._state_lock:
            if field_id not in self.managed_fields:
                return None
            
            field = self.managed_fields[field_id]
            return {
                'field_id': field_id,
                'field_type': field.field_type.value,
                'state_count': len(field.field_states),
                'states': list(field.field_states.keys()),
                'field_energy': field.field_energy,
                'transitions_made': field.state_transitions
            }
    
    def _setup_alt_las_integration(self):
        """Setup ALT_LAS integration"""
        try:
            from ..computer_access.vision.q02_quantum_seed_integration import QuantumSeedManager
            self.alt_las_integration_active = True
            self.logger.info("🔗 ALT_LAS integration activated")
        except ImportError:
            self.logger.warning("⚠️ ALT_LAS integration not available")
    
    def _register_default_transition_rules(self):
        """Register default transition rules"""
        # Default rules for common transitions
        self.transition_rules['decoherence'] = self._apply_decoherence
        self.transition_rules['spontaneous_emission'] = self._apply_spontaneous_emission
        self.logger.debug("📋 Default transition rules registered")
    
    def _create_default_observer(self):
        """Create default quantum observer"""
        default_observer = QuantumObserver(
            observer_type=ObserverType.PASSIVE,
            name="Default QFD Observer",
            measurement_strength=0.5,
            decoherence_rate=0.05
        )
        self.register_observer(default_observer)
    
    def _apply_decoherence(self, state: QuantumState) -> bool:
        """Apply decoherence to quantum state"""
        state.coherence *= 0.95  # Gradual decoherence
        return True
    
    def _apply_spontaneous_emission(self, state: QuantumState) -> bool:
        """Apply spontaneous emission"""
        if len(state.amplitudes) > 1:
            # Transfer amplitude from excited to ground state
            excited_amp = state.amplitudes[1] if len(state.amplitudes) > 1 else 0
            state.amplitudes[0] += excited_amp * 0.1
            if len(state.amplitudes) > 1:
                state.amplitudes[1] *= 0.9
            state.normalize()
        return True

# Utility functions
def create_field_state_manager(config: Optional[QFDConfig] = None) -> FieldStateManager:
    """Create a new field state manager"""
    return FieldStateManager(config)

def create_quantum_observer(observer_type: ObserverType = ObserverType.PASSIVE,
                           name: str = "Quantum Observer") -> QuantumObserver:
    """Create a new quantum observer"""
    return QuantumObserver(observer_type=observer_type, name=name)

def test_field_state_manager():
    """Test field state manager functionality"""
    print("🔮 Testing Field State Manager...")
    
    # Create manager
    manager = create_field_state_manager()
    print("✅ Field state manager created")
    
    # Initialize
    if manager.initialize():
        print("✅ Manager initialized successfully")
    
    # Create and register a field
    from .quantum_field import create_quantum_field, FieldType, FieldDimension
    field = create_quantum_field(FieldType.SCALAR, FieldDimension.THREE_D)
    field.initialize()
    
    if manager.register_field(field):
        print("✅ Field registered successfully")
    
    # Create observer
    observer = create_quantum_observer(ObserverType.ACTIVE, "Test Observer")
    if manager.register_observer(observer):
        print("✅ Observer registered successfully")
    
    # Trigger transition
    transition = manager.trigger_state_transition(
        field.field_id, "default", "excited",
        TransitionType.INDUCED, observer.observer_id
    )
    
    if transition:
        print(f"✅ State transition successful: {transition.transition_id[:16]}...")
    
    # Get status
    status = manager.get_status()
    print(f"✅ Manager status: {status['successful_transitions']} successful transitions")
    
    print("🚀 Field State Manager test completed!")

if __name__ == "__main__":
    test_field_state_manager()
