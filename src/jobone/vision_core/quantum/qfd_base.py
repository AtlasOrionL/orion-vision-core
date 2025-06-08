"""
🔮 QFD Base Classes - Q05.1.1 Component

Quantum Field Dynamics temel sınıfları ve interface'leri.
ALT_LAS Quantum Mind OS ile entegre çalışır.

Bu modül Q05.1.1 görevinin ilk parçasıdır:
- QFD base classes ✅
- Quantum entity abstractions
- Configuration management
- Exception handling

Author: Orion Vision Core Team
Sprint: Q05.1.1 - QFD Temel Altyapısı
Status: IMPLEMENTED
"""

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable
import threading
import json

# QFD Configuration
@dataclass
class QFDConfig:
    """QFD sistem konfigürasyonu"""
    
    # Quantum field parameters
    field_dimensions: int = 3
    max_superposition_states: int = 8
    quantum_coherence_threshold: float = 0.95
    entanglement_fidelity_min: float = 0.90
    
    # Performance settings
    calculation_timeout: float = 1.0  # ms
    max_concurrent_operations: int = 100
    memory_limit_mb: int = 512
    
    # ALT_LAS integration
    alt_las_integration: bool = True
    quantum_seed_integration: bool = True
    atlas_memory_sync: bool = True
    
    # Logging and monitoring
    log_level: str = "INFO"
    performance_monitoring: bool = True
    quantum_state_logging: bool = True
    
    # Q01-Q04 compatibility
    backward_compatibility: bool = True
    legacy_mode: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'field_dimensions': self.field_dimensions,
            'max_superposition_states': self.max_superposition_states,
            'quantum_coherence_threshold': self.quantum_coherence_threshold,
            'entanglement_fidelity_min': self.entanglement_fidelity_min,
            'calculation_timeout': self.calculation_timeout,
            'max_concurrent_operations': self.max_concurrent_operations,
            'memory_limit_mb': self.memory_limit_mb,
            'alt_las_integration': self.alt_las_integration,
            'quantum_seed_integration': self.quantum_seed_integration,
            'atlas_memory_sync': self.atlas_memory_sync,
            'log_level': self.log_level,
            'performance_monitoring': self.performance_monitoring,
            'quantum_state_logging': self.quantum_state_logging,
            'backward_compatibility': self.backward_compatibility,
            'legacy_mode': self.legacy_mode
        }

# QFD Exception Classes
class QFDException(Exception):
    """Base QFD exception"""
    pass

class QuantumStateError(QFDException):
    """Quantum state related errors"""
    pass

class FieldCalculationError(QFDException):
    """Field calculation errors"""
    pass

class IntegrationError(QFDException):
    """ALT_LAS integration errors"""
    pass

# Quantum Entity Types
class EntityType(Enum):
    """Kuantum varlık türleri"""
    LEPTON = "lepton"
    QCB = "qcb"
    FIELD = "field"
    OBSERVER = "observer"
    CALCULATOR = "calculator"

# Base Quantum Entity
@dataclass
class QuantumEntity:
    """Temel kuantum varlığı"""
    
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType = EntityType.FIELD
    created_at: datetime = field(default_factory=datetime.now)
    
    # Quantum properties
    quantum_state: Optional[Dict[str, Any]] = None
    superposition_active: bool = False
    entangled_entities: List[str] = field(default_factory=list)
    
    # ALT_LAS integration
    alt_las_seed: Optional[str] = None
    atlas_memory_ref: Optional[str] = None
    
    # Performance metrics
    operation_count: int = 0
    last_operation: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization setup"""
        if self.quantum_state is None:
            self.quantum_state = {
                'amplitude': 1.0,
                'phase': 0.0,
                'coherence': 1.0,
                'measurement_count': 0
            }
    
    def update_state(self, new_state: Dict[str, Any]) -> bool:
        """Update quantum state"""
        try:
            if self.quantum_state:
                self.quantum_state.update(new_state)
                self.last_operation = datetime.now()
                self.operation_count += 1
                return True
            return False
        except Exception:
            return False
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get quantum state summary"""
        return {
            'entity_id': self.entity_id[:16] + "...",
            'type': self.entity_type.value,
            'superposition': self.superposition_active,
            'entangled_count': len(self.entangled_entities),
            'operations': self.operation_count,
            'coherence': self.quantum_state.get('coherence', 0.0) if self.quantum_state else 0.0
        }

# Abstract QFD Base Class
class QFDBase(ABC):
    """
    QFD sistemlerinin temel abstract sınıfı
    
    Tüm QFD bileşenleri bu sınıftan türetilir:
    - QuantumField
    - FieldStateManager  
    - QuantumCalculator
    - QFDIntegrator
    """
    
    def __init__(self, config: Optional[QFDConfig] = None):
        self.config = config or QFDConfig()
        self.logger = logging.getLogger(f'qfd.{self.__class__.__name__.lower()}')
        self.logger.setLevel(getattr(logging, self.config.log_level))
        
        # Base properties
        self.component_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.initialized = False
        self.active = False
        
        # Performance tracking
        self.operation_metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'average_duration': 0.0,
            'last_operation_time': None
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        self.logger.info(f"🔮 {self.__class__.__name__} initialized")
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the QFD component"""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown the QFD component"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get component status"""
        pass
    
    def _update_metrics(self, operation_name: str, duration: float, success: bool):
        """Update performance metrics"""
        with self._lock:
            self.operation_metrics['total_operations'] += 1
            if success:
                self.operation_metrics['successful_operations'] += 1
            else:
                self.operation_metrics['failed_operations'] += 1
            
            # Update average duration
            total_ops = self.operation_metrics['total_operations']
            current_avg = self.operation_metrics['average_duration']
            self.operation_metrics['average_duration'] = (
                (current_avg * (total_ops - 1) + duration) / total_ops
            )
            
            self.operation_metrics['last_operation_time'] = datetime.now()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        with self._lock:
            return self.operation_metrics.copy()
    
    def validate_config(self) -> bool:
        """Validate QFD configuration"""
        try:
            # Check required parameters
            if self.config.field_dimensions < 1:
                raise ValueError("field_dimensions must be >= 1")
            
            if not (0.0 <= self.config.quantum_coherence_threshold <= 1.0):
                raise ValueError("quantum_coherence_threshold must be between 0.0 and 1.0")
            
            if not (0.0 <= self.config.entanglement_fidelity_min <= 1.0):
                raise ValueError("entanglement_fidelity_min must be between 0.0 and 1.0")
            
            if self.config.calculation_timeout <= 0:
                raise ValueError("calculation_timeout must be > 0")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Config validation failed: {e}")
            return False
    
    def check_alt_las_integration(self) -> bool:
        """Check ALT_LAS integration availability"""
        if not self.config.alt_las_integration:
            return True  # Integration disabled, so it's "available"
        
        try:
            # Try to import ALT_LAS components
            from ..computer_access.vision.alt_las_quantum_mind_os import ALTLASQuantumMindOS
            from ..computer_access.vision.q02_quantum_seed_integration import QuantumSeedManager
            return True
        except ImportError:
            self.logger.warning("⚠️ ALT_LAS components not available")
            return False
    
    def log_quantum_operation(self, operation: str, details: Dict[str, Any]):
        """Log quantum operation for debugging"""
        if self.config.quantum_state_logging:
            self.logger.debug(f"🔮 Quantum Operation: {operation}")
            self.logger.debug(f"📊 Details: {json.dumps(details, default=str, indent=2)}")

# QFD Component Registry
class QFDRegistry:
    """QFD bileşen kayıt sistemi"""
    
    def __init__(self):
        self.components: Dict[str, QFDBase] = {}
        self.logger = logging.getLogger('qfd.registry')
        self._lock = threading.Lock()
    
    def register_component(self, name: str, component: QFDBase) -> bool:
        """Register a QFD component"""
        try:
            with self._lock:
                self.components[name] = component
                self.logger.info(f"✅ Registered QFD component: {name}")
                return True
        except Exception as e:
            self.logger.error(f"❌ Failed to register component {name}: {e}")
            return False
    
    def get_component(self, name: str) -> Optional[QFDBase]:
        """Get a registered component"""
        with self._lock:
            return self.components.get(name)
    
    def list_components(self) -> List[str]:
        """List all registered components"""
        with self._lock:
            return list(self.components.keys())
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        with self._lock:
            status = {
                'total_components': len(self.components),
                'active_components': 0,
                'components': {}
            }
            
            for name, component in self.components.items():
                comp_status = component.get_status()
                status['components'][name] = comp_status
                if comp_status.get('active', False):
                    status['active_components'] += 1
            
            return status

# Global QFD registry instance
qfd_registry = QFDRegistry()

# Utility functions
def create_quantum_entity(entity_type: EntityType, **kwargs) -> QuantumEntity:
    """Create a new quantum entity"""
    return QuantumEntity(entity_type=entity_type, **kwargs)

def validate_quantum_state(state: Dict[str, Any]) -> bool:
    """Validate quantum state dictionary"""
    required_keys = ['amplitude', 'phase', 'coherence']
    return all(key in state for key in required_keys)

# Module test function
def test_qfd_base():
    """Test QFD base functionality"""
    print("🔮 Testing QFD Base Classes...")
    
    # Test config
    config = QFDConfig()
    print(f"✅ Config created: {config.field_dimensions}D fields")
    
    # Test quantum entity
    entity = create_quantum_entity(EntityType.LEPTON)
    print(f"✅ Quantum entity created: {entity.entity_id[:16]}...")
    
    # Test state update
    entity.update_state({'amplitude': 0.8, 'phase': 1.57})
    print(f"✅ State updated: coherence={entity.quantum_state['coherence']}")
    
    print("🚀 QFD Base Classes test completed!")

if __name__ == "__main__":
    test_qfd_base()
