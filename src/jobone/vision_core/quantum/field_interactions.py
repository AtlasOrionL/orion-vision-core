"""
⚛️ Field Interaction Modeling - Q05.3.1 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Q05.3.1 Field Interaction Modeling
Priority: CRITICAL - Modular Design Refactoring Phase 12
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional

# Import core components from modular design
from .modules.field_dynamics.field_interactions_core import (
    InteractionType, CouplingMechanism, InteractionParameters, InteractionResult,
    create_interaction_parameters, create_interaction_result, estimate_interaction_time
)

# Import engine component
from .modules.field_dynamics.field_interactions_engine import (
    FieldInteractionEngine
)

# Import statistics component
from .modules.field_dynamics.field_interactions_statistics import (
    FieldInteractionStatistics, get_field_interaction_statistics,
    create_field_interaction_statistics, analyze_interaction_batch,
    get_interaction_summary, get_parameters_summary, compare_interaction_types
)

# Enhanced Field Interaction Modeler with statistics
class FieldInteractionModeler:
    """
    Enhanced Field Interaction Modeler with integrated statistics
    
    Unified interface for field interaction modeling with modular design
    """
    
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize components
        self.engine = FieldInteractionEngine()
        self.statistics = create_field_interaction_statistics()
        
        # Interaction management
        self.interaction_results: List[InteractionResult] = []
        self.active_interactions: Dict[str, InteractionResult] = {}
        
        # Performance tracking
        self.total_interactions = 0
        self.successful_interactions = 0
        self.failed_interactions = 0
        
        # ALT_LAS integration
        self.alt_las_integration_active = False
        self.consciousness_interaction_enabled = False
        
        # Threading
        self._interaction_lock = threading.Lock()
        self._results_lock = threading.Lock()
        
        # Status
        self.initialized = False
        self.active = False
        
        self.logger.info("⚛️ FieldInteractionModeler initialized with modular design")
    
    def initialize(self) -> bool:
        """Initialize field interaction modeler"""
        try:
            self.initialized = True
            self.active = True
            
            self.logger.info("✅ FieldInteractionModeler initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ FieldInteractionModeler initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown field interaction modeler"""
        try:
            self.active = False
            
            with self._interaction_lock:
                self.active_interactions.clear()
            
            self.logger.info("🔴 FieldInteractionModeler shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ FieldInteractionModeler shutdown failed: {e}")
            return False
    
    def model_field_interaction(self, field_states: List[Any], 
                               parameters: InteractionParameters) -> Optional[InteractionResult]:
        """Model interaction between quantum fields"""
        try:
            # Use engine for interaction modeling
            result = self.engine.process_field_interaction(field_states, parameters)
            
            if result:
                # Add to statistics
                self.statistics.add_interaction_result(result, parameters)
                
                # Store result
                with self._results_lock:
                    self.interaction_results.append(result)
                    # Keep history manageable
                    if len(self.interaction_results) > 1000:
                        self.interaction_results = self.interaction_results[-500:]
                
                # Update counters
                self.total_interactions += 1
                if result.interaction_successful:
                    self.successful_interactions += 1
                else:
                    self.failed_interactions += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Field interaction modeling failed: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status"""
        with self._interaction_lock, self._results_lock:
            engine_stats = self.engine.get_engine_statistics()
            interaction_stats = self.statistics.get_comprehensive_statistics()
            
            return {
                'initialized': self.initialized,
                'active': self.active,
                'total_interactions': self.total_interactions,
                'successful_interactions': self.successful_interactions,
                'failed_interactions': self.failed_interactions,
                'success_rate': (self.successful_interactions / max(1, self.total_interactions)) * 100,
                'interaction_history_size': len(self.interaction_results),
                'active_interactions': len(self.active_interactions),
                'alt_las_integration': self.alt_las_integration_active,
                'consciousness_interaction': self.consciousness_interaction_enabled,
                'engine_statistics': engine_stats,
                'interaction_statistics': interaction_stats
            }
    
    def get_field_interaction_statistics(self):
        """Get comprehensive field interaction statistics"""
        return self.statistics.get_comprehensive_statistics()

# Utility functions
def create_field_interaction_modeler(config=None) -> FieldInteractionModeler:
    """Create Field Interaction Modeler system"""
    return FieldInteractionModeler(config)

def test_field_interaction_modeler():
    """Test Field Interaction Modeler system"""
    print("⚛️ Testing Field Interaction Modeler...")
    
    # Create modeler
    modeler = create_field_interaction_modeler()
    modeler.initialize()
    print("✅ Field interaction modeler created")
    
    # Test interaction types
    interaction_types = list(InteractionType)
    print(f"✅ Available interaction types: {[itype.value for itype in interaction_types]}")
    
    # Test coupling mechanisms
    coupling_mechanisms = list(CouplingMechanism)
    print(f"✅ Available coupling mechanisms: {[mech.value for mech in coupling_mechanisms]}")
    
    # Get comprehensive status
    status = modeler.get_status()
    print(f"✅ Modeler Status:")
    print(f"    - Total interactions: {status['total_interactions']}")
    print(f"    - Success rate: {status['success_rate']:.1f}%")
    print(f"    - ALT_LAS integration: {status['alt_las_integration']}")
    
    print("🚀 Field Interaction Modeler test completed!")

# Export all components for backward compatibility
__all__ = [
    'InteractionType',
    'CouplingMechanism',
    'InteractionParameters',
    'InteractionResult',
    'FieldInteractionModeler',
    'FieldInteractionEngine',
    'FieldInteractionStatistics',
    'create_interaction_parameters',
    'create_interaction_result',
    'estimate_interaction_time',
    'create_field_interaction_modeler',
    'get_field_interaction_statistics',
    'create_field_interaction_statistics',
    'analyze_interaction_batch',
    'get_interaction_summary',
    'get_parameters_summary',
    'compare_interaction_types',
    'test_field_interaction_modeler'
]

if __name__ == "__main__":
    test_field_interaction_modeler()
