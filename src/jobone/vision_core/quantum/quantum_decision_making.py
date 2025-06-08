"""
🧠 Quantum Decision Making - Q05.4.1 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Q05.4.1 Quantum Decision Making
Priority: CRITICAL - Modular Design Refactoring Phase 13
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional

# Import core components from modular design
from .modules.measurement.decision_making_core import (
    DecisionType, DecisionMethod, DecisionParameters, DecisionResult,
    create_decision_parameters, create_decision_result, estimate_decision_time
)

# Import engine component
from .modules.measurement.decision_making_engine import (
    DecisionMakingEngine
)

# Import statistics component
from .modules.measurement.decision_making_statistics import (
    DecisionMakingStatistics, get_decision_making_statistics,
    create_decision_making_statistics, analyze_decision_batch,
    get_decision_summary, get_parameters_summary, compare_decision_methods
)

# Enhanced Quantum Decision Maker with statistics
class QuantumDecisionMaker:
    """
    Enhanced Quantum Decision Maker with integrated statistics
    
    Unified interface for quantum decision making with modular design
    """
    
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize components
        self.engine = DecisionMakingEngine()
        self.statistics = create_decision_making_statistics()
        
        # Decision management
        self.decision_results: List[DecisionResult] = []
        self.active_decisions: Dict[str, DecisionResult] = {}
        
        # Performance tracking
        self.total_decisions = 0
        self.successful_decisions = 0
        self.failed_decisions = 0
        
        # Integration components (simplified)
        self.alt_las_interface = None
        self.consciousness_simulator = None
        
        # Threading
        self._decision_lock = threading.Lock()
        self._results_lock = threading.Lock()
        
        # Status
        self.initialized = False
        self.active = False
        
        self.logger.info("🧠 QuantumDecisionMaker initialized with modular design")
    
    def initialize(self) -> bool:
        """Initialize quantum decision maker"""
        try:
            self.initialized = True
            self.active = True
            
            self.logger.info("✅ QuantumDecisionMaker initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ QuantumDecisionMaker initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown quantum decision maker"""
        try:
            self.active = False
            
            with self._decision_lock:
                self.active_decisions.clear()
            
            self.logger.info("🔴 QuantumDecisionMaker shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ QuantumDecisionMaker shutdown failed: {e}")
            return False
    
    def make_decision(self, parameters: DecisionParameters) -> Optional[DecisionResult]:
        """Make quantum-enhanced decision"""
        try:
            # Use engine for decision making
            result = self.engine.process_decision(parameters)
            
            if result:
                # Add to statistics
                self.statistics.add_decision_result(result, parameters)
                
                # Store result
                with self._results_lock:
                    self.decision_results.append(result)
                    # Keep history manageable
                    if len(self.decision_results) > 1000:
                        self.decision_results = self.decision_results[-500:]
                
                # Update counters
                self.total_decisions += 1
                if result.chosen_option:
                    self.successful_decisions += 1
                else:
                    self.failed_decisions += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Decision making failed: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status"""
        with self._decision_lock, self._results_lock:
            engine_stats = self.engine.get_engine_statistics()
            decision_stats = self.statistics.get_comprehensive_statistics()
            
            return {
                'initialized': self.initialized,
                'active': self.active,
                'total_decisions': self.total_decisions,
                'successful_decisions': self.successful_decisions,
                'failed_decisions': self.failed_decisions,
                'success_rate': (self.successful_decisions / max(1, self.total_decisions)) * 100,
                'decision_history_size': len(self.decision_results),
                'active_decisions': len(self.active_decisions),
                'alt_las_interface_active': self.alt_las_interface is not None,
                'consciousness_simulator_active': self.consciousness_simulator is not None,
                'engine_statistics': engine_stats,
                'decision_statistics': decision_stats
            }
    
    def get_decision_making_statistics(self):
        """Get comprehensive decision making statistics"""
        return self.statistics.get_comprehensive_statistics()

# Utility functions
def create_quantum_decision_maker(config=None) -> QuantumDecisionMaker:
    """Create Quantum Decision Maker system"""
    return QuantumDecisionMaker(config)

def test_quantum_decision_maker():
    """Test Quantum Decision Maker system"""
    print("🧠 Testing Quantum Decision Maker...")
    
    # Create decision maker
    decision_maker = create_quantum_decision_maker()
    decision_maker.initialize()
    print("✅ Quantum decision maker created")
    
    # Test decision types
    decision_types = list(DecisionType)
    print(f"✅ Available decision types: {[dtype.value for dtype in decision_types]}")
    
    # Test decision methods
    decision_methods = list(DecisionMethod)
    print(f"✅ Available decision methods: {[method.value for method in decision_methods]}")
    
    # Test simple decision
    parameters = create_decision_parameters(
        decision_type=DecisionType.BINARY,
        decision_method=DecisionMethod.QUANTUM_SUPERPOSITION,
        decision_question="Should we proceed with Phase 13?",
        available_options=["Yes", "No"]
    )
    
    result = decision_maker.make_decision(parameters)
    if result:
        print(f"✅ Test Decision Result:")
        print(f"    - Chosen option: {result.chosen_option}")
        print(f"    - Confidence: {result.decision_confidence:.1%}")
        print(f"    - Quality: {result.analysis_quality:.3f}")
    
    # Get comprehensive status
    status = decision_maker.get_status()
    print(f"✅ Decision Maker Status:")
    print(f"    - Total decisions: {status['total_decisions']}")
    print(f"    - Success rate: {status['success_rate']:.1f}%")
    
    print("🚀 Quantum Decision Maker test completed!")

# Export all components for backward compatibility
__all__ = [
    'DecisionType',
    'DecisionMethod',
    'DecisionParameters',
    'DecisionResult',
    'QuantumDecisionMaker',
    'DecisionMakingEngine',
    'DecisionMakingStatistics',
    'create_decision_parameters',
    'create_decision_result',
    'estimate_decision_time',
    'create_quantum_decision_maker',
    'get_decision_making_statistics',
    'create_decision_making_statistics',
    'analyze_decision_batch',
    'get_decision_summary',
    'get_parameters_summary',
    'compare_decision_methods',
    'test_quantum_decision_maker'
]

if __name__ == "__main__":
    test_quantum_decision_maker()
